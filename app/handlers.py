import logging
from concurrent.futures import ThreadPoolExecutor

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import app.database_actions as base
import app.scrapping_actions as sa

router = Router()


class User(StatesGroup):
    login = State()
    password = State()
    link_to_post = State()
    last_state = State()


executor = ThreadPoolExecutor(max_workers=2)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hi!\nI'm your bot.\nUse /get_data to start.")


@router.message(Command('get_data'))
async def get_data(message: Message, state: FSMContext):
    await state.set_state(User.link_to_post)
    await message.answer('Provide link to post')


@router.message(User.link_to_post)
async def comment_post(message: Message, state: FSMContext):
    await state.update_data(link_to_post=message.text)
    await state.set_state(User.login)
    await message.answer('Provide login to your twitter account')


@router.message(User.login)
async def comment_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await state.set_state(User.password)
    await message.answer('Provide password to your twitter account')


@router.message(User.password)
async def comment_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    base.insert_user_information(data, message.from_user.id)
    logging.info("Entering comment_password handler")
    await message.answer('Thank u for provided information')
    await state.clear()


@router.message(Command('generate_comment'))
async def generate_comment(message: Message):
    user_id = str(message.from_user.id)
    data = base.get_user_information(user_id)
    await message.answer('We are generating your comment, please wait...')

    await sa.twitter_scraping(data, user_id)
    await message.answer('Your comment was generated!')


@router.message(Command('show_comment'))
async def show_generated_comment(message: Message):
    comment = base.get_comment(str(message.from_user.id))
    await message.answer(f'Generated comment: \n\n{comment["COMMENT"]}')


@router.message(Command('show_post_information'))
async def show_post_information(message: Message):
    post = base.get_post_information(str(message.from_user.id))
    formatted_lines = []
    for key, value in post.items():
        if key == 'CreatorAccount':
            key = 'Creator Account'
        if key == 'HasPhoto':
            continue
        if key == 'Photo' and post.get('HasPhoto') == 0:
            continue
        if key == 'Photo' and post.get('HasPhoto') == 1:
            key = 'PhotoPath'

        if key in ['Comments', 'Reposts', 'Likes', 'Views', 'Bookmarks']:
            key += ' amount'
            if value == '':
                continue

        formatted_lines.append(f'• {key}: {value}')

    formatted_post = '\n'.join(formatted_lines)
    await message.answer(f'Information from your post is next: \n\n{formatted_post}')


@router.message(Command('share_comment'))
async def share_comment(message: Message):
    answer = await sa.insert_comment(str(message.from_user.id))
    await message.answer(answer)


@router.message(Command('like_post'))
async def generate_like(message: Message):
    answer = await sa.make_an_activity(str(message.from_user.id), 'like')
    await message.answer(answer)


@router.message(Command('bookmark_post'))
async def generate_bookmark(message: Message):
    answer = await sa.make_an_activity(str(message.from_user.id), 'bookmark')
    await message.answer(answer)


@router.message(Command('retweet_post'))
async def generate_retweet(message: Message):
    answer = await sa.make_an_activity(str(message.from_user.id), 'retweet')
    await message.answer(answer)