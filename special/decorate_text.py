from aiogram import html


async def blockquote(text):
    quote_text = html.quote(text)
    return html.blockquote(quote_text)

