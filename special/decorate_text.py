from aiogram import html


async def blockquote(text):
    quote_text = html.quote(text)
    return html.blockquote(quote_text)


def exp_bl(text):
    quote_text = html.quote(text)
    return html.blockquote(quote_text)


def link(text, text_link):
    quote_text = html.quote(text)
    return html.link(quote_text, text_link)
