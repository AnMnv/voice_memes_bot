from config import TOKEN

from aiogram import Bot, types
from aiogram. dispatcher import Dispatcher
from aiogram.utils import executor
import os, hashlib
import json
import pickledb

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle
from aiogram.types import (InputTextMessageContent, 
    InlineQueryResultArticle, 
    InlineQueryResultCachedAudio, 
    InlineQueryResultAudio, 
    InputMessageContent, 
    InlineQueryResultPhoto,
    InlineQueryResultVoice)
from aiogram.types.input_media import InputMediaAudio


bot = Bot (token =  TOKEN)
dp = Dispatcher(bot)

usersID = pickledb.load('usersID.db', False)
 





# Load the audio database from a JSON file
with open('db.json', 'r', encoding="utf-8") as f:
    audio_db = json.load(f)

@dp.message_handler(commands=['whosentphotos'])
async def command(message):
    with open('usersID.db', 'r') as handle:
        parsed = json.load(handle)

    f = open("usersID.csv", "w")
    for s in parsed:
        f.write(s + "," + parsed[s] + "\n")
    f.close()

    doc = open('usersID.csv', 'rb')
    usersID_db = open('usersID.db', 'rb')
    await bot.send_document(chat_id=message.chat.id, document=doc)
    await bot.send_document(chat_id=message.chat.id, document=usersID_db)

@dp.inline_handler()
async def inline_handler(query: types.InlineQuery):



    # Get the user's input text and tags
    input_text = query.query
    tags = input_text.split()

    # Search for the audio files in the database
    results = []
    if tags != []:
        for audio in audio_db:
            if all(tag in audio['tags'] for tag in tags):
                audio_file = audio['audio']
                result_id: str = hashlib.md5(audio_file.encode()).hexdigest()
                result = InlineQueryResultVoice(
                    id=result_id,
                    voice_url=audio_file,
                    title=audio['title'],
                    input_message_content=InputMessageContent(audio_file)
                )
                results.append(result)
                audio['usage_count'] += 1
                with open('db.json', 'w', encoding="utf-8") as f:
                    json.dump(audio_db, f,indent=4, sort_keys=True, ensure_ascii=False)
                    


    if results:
        user = query.from_user
        print(f"User {user.username} made an inline query: {query.query}")

        usersID_counter = usersID.get(str(f'@{query.from_user.username} {query.from_user.id}'))
        if usersID_counter == False:
            usersID.set(str(f'@{query.from_user.username} {query.from_user.id}'), '1')
        else:
            usersID.set(str(f'@{query.from_user.username} {query.from_user.id}'), str(int(usersID_counter) + 1))
        usersID.dump()
        await query.answer(results=results, cache_time=0)

    else:
        audio_results = []
        if tags == []:
            # Create a list of audio results
            for audio in audio_db:
                audio_file = audio['audio']
                result_id: str = hashlib.md5(audio_file.encode()).hexdigest()
                result = InlineQueryResultAudio(
                    id=result_id,
                    audio_url=audio_file,
                    title=audio['title'],
                    performer=str(f"использовали {audio['usage_count']} раз")
                )
                audio_results.append(result)

            # Split the audio results into batches
            batch_size = 40
            offset = int(query.offset) if query.offset else 0
            results = audio_results[offset:offset + batch_size]

            # Calculate the next offset for pagination
            next_offset = str(offset + batch_size) if offset + batch_size < len(audio_results) else ''

            # Create the inline keyboard with the button to the website
            #inline_kb = InlineKeyboardMarkup()
            #inline_kb.add(InlineKeyboardButton(text='Заказать рекламу', url='https://t.me/notjustmemebot'))

            # Add the article result with the photo and inline keyboard to the beginning of the list
            await query.answer(
                #results=[
                #    InlineQueryResultArticle(
                #        id='article_result',
                #        title='Список аудиозаписей',
                #        description='Заказать рекламу',
                #        thumb_url='https://i.postimg.cc/NFMcyxXG/Screenshot-2023-05-15-160307.png',
                #        input_message_content=InputTextMessageContent(
                #            message_text='Список аудиозаписей:'
                #        ),
                #        reply_markup=inline_kb
                #    )
                #] + 
                results,
                cache_time=0,
                next_offset=next_offset
            )





executor.start_polling(dp, skip_updates=True)