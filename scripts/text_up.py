import os
import textwrap

from PIL import Image, ImageDraw, ImageFont


def text_up(name, mes):
    # адрес хранения пикчи
    pic_name = name

    # текст, который надо вставить сверху
    txt_msg = mes

    pic = Image.open(pic_name)

    width, height = pic.size

    # Определите максимальную ширину текста и разделите текст на несколько строк
    max_width = 40
    lines = textwrap.wrap(txt_msg, width=max_width)

    max_size = 1/8 * height
    max_len = max(len(line) for line in lines)

    size = int((width * 0.9) / max(len(line) for line in lines) / 0.6)
    if size > max_size:
        size = max_size

    font = ImageFont.truetype('fonts/Attractive-Heavy.ttf', size=size)
    for line in lines:
        if len(line) == max_len:
            max_line = line
            break

    w_text = font.getmask(max_line).getbbox()[2]
    while w_text > 0.9 * width:
            size -= 0.01 * size
            font = ImageFont.truetype('fonts/Attractive-Heavy.ttf', size=size)
            w_text = font.getmask(max_line).getbbox()[2]

    line_height = sum(font.getmetrics())

    # Определите начальную координату y так, чтобы текст всегда был на одинаковом расстоянии от верхнего края изображения
    y = int(height * 0.03)

    for line in lines:
        w_text = font.getmask(line).getbbox()[2]
        font_image = Image.new('L', (w_text, line_height))
        ImageDraw.Draw(font_image).text((0, 0), line, fill=255, font=font)
        font_image = font_image.rotate(0, resample=Image.BICUBIC, expand=True)

        x = (width - w_text) // 2

        for i in range(3):
            pic.paste((0, 0, 0), (x - i, y), mask=font_image)
            pic.paste((0, 0, 0), (x + i, y), mask=font_image)
            pic.paste((0, 0, 0), (x, y + i), mask=font_image)
            pic.paste((0, 0, 0), (x, y - i), mask=font_image)
            pic.paste((0, 0, 0), (x - i, y + i), mask=font_image)
            pic.paste((0, 0, 0), (x + i, y + i), mask=font_image)
            pic.paste((0, 0, 0), (x - i, y - i), mask=font_image)
            pic.paste((0, 0, 0), (x + i, y - i), mask=font_image)
        pic.paste((255, 255, 255), (x, y), mask=font_image)

        # Переход к следующей строке
        y += line_height

    os.remove(pic_name)
    pic.save(pic_name, quality=95)

    return pic_name  # возвращает адрес к пикче, а не саму пикчу
