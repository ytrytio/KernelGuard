from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultPhoto
from uuid import uuid4
import aiohttp

router = Router(name=__name__)

@router.inline_query()
async def inline_handler(inline_query: InlineQuery):
    results = []
    user_text = inline_query.query.strip()
    query_param = user_text if user_text else ""

    async with aiohttp.ClientSession() as session:
        """
        try:
            cat_api_url = f"https://api.thecatapi.com/v1/images/search?limit=3{query_param}"
            async with session.get(cat_api_url) as r_cat:
                cat_data = await r_cat.json()
                for cat in cat_data:
                    cat_url = cat["url"]
                    results.append(
                        InlineQueryResultPhoto(
                            id=str(uuid4()),
                            photo_url=cat_url,
                            thumbnail_url=cat_url
                        )
                    )
        except Exception as e:
            print(f"Cat error: {e}")
        """

        # --- 2. NEKO ---
        try:
            if query_param != "":
                neko_api_url = f"https://nekos.best/api/v2/search?query={query_param}&type=1&category=neko&amount=10"
            else:
                neko_api_url = f"https://nekos.best/api/v2/neko?amount=10"
            
            async with session.get(neko_api_url) as r_neko:
                data = await r_neko.json()
                neko_data = data.get('results', [])
                for req in neko_data:
                    neko_url = req['url']
                    neko_artist = req.get('artist_name', 'Unknown')
                    results.append(
                        InlineQueryResultPhoto(
                            id=str(uuid4()),
                            photo_url=neko_url,
                            thumbnail_url=neko_url,
                            caption=f"<blockquote><i>by <b>{neko_artist}</b></i></blockquote>",
                            parse_mode="HTML"
                        )
                    )
        except Exception as e:
            print(f"Neko error: {e}")

        # --- 3. WAIFU ---
        try:
            if query_param != "":
                waifu_api_url = f"https://nekos.best/api/v2/search?query={query_param}&type=1&category=waifu&amount=10"
            else:
                waifu_api_url = f"https://nekos.best/api/v2/waifu?amount=10"
            
            async with session.get(waifu_api_url) as r_waifu:
                data = await r_waifu.json()
                waifu_data = data.get('results', [])
                for req in waifu_data:
                    waifu_url = req['url']
                    waifu_artist = req.get('artist_name', 'Unknown')
                    results.append(
                        InlineQueryResultPhoto(
                            id=str(uuid4()),
                            photo_url=waifu_url,
                            thumbnail_url=waifu_url,
                            caption=f"<blockquote><i>by <b>{waifu_artist}</b></i></blockquote>",
                            parse_mode="HTML"
                        )
                    )
        except Exception as e:
            print(f"Waifu error: {e}")

    await inline_query.answer(results, is_personal=True, cache_time=1)
