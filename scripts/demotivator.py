from PIL import ImageOps
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont


def mem_ramka(name, mes_up, mes_down):
    # адрес хранения пикчи
    pic_name = name

    pic = Image.open(pic_name)
    width, height = pic.size

    # текст для верхнего
    text__demotivator_up = mes_up

    if text__demotivator_up:
        # # Определите максимальную ширину текста и разделите текст на несколько строк
        # max_width = 40
        # lines_up = textwrap.wrap(text__demotivator_up, width=max_width)
        # # Определите размер шрифта на основе ширины изображения
        # max_size = 1 / 6 * width
        # size_up = int((width - 0.01 * width) / max(len(line) for line in lines_up) / 0.48)
        # if size_up > max_size:
        #     size_up = max_size
        #
        # font_up = ImageFont.truetype('fonts/timesnewromanpsmt.ttf', size=size_up)

        # Определите максимальную ширину текста и разделите текст на несколько строк
        max_width = 40
        lines_up = textwrap.wrap(text__demotivator_up, width=max_width)

        max_size = 1 / 5 * height
        max_len_up = max(len(line) for line in lines_up)

        size = int((width * 0.9) / max(len(line) for line in lines_up) / 0.48)
        if size > max_size:
            size = max_size

        font_up = ImageFont.truetype('fonts/timesnewromanpsmt.ttf', size=size)
        for line in lines_up:
            if len(line) == max_len_up:
                max_line_up = line
                break

        w_text = font_up.getmask(max_line_up).getbbox()[2]
        while w_text > 0.95 * width:
            size -= 0.01 * size
            font_up = ImageFont.truetype('fonts/timesnewromanpsmt.ttf', size=size)
            w_text = font_up.getmask(max_line_up).getbbox()[2]

        line_height_up = sum(font_up.getmetrics())

    else:
        line_height_up = 0
        lines_up = []

    # текст для нижнего
    text__demotivator_down = mes_down

    if text__demotivator_down:
        # # Максимальная ширина текста и разделите текст на несколько строк
        # max_width = 40
        # lines_down = textwrap.wrap(text__demotivator_down, width=max_width)
        #
        # # Размер шрифта на основе ширины изображения
        # max_size = 1 / 10 * width
        # size_down = int((width - 0.01 * width) / max(len(line) for line in lines_down) / 0.6)
        # if size_down > max_size:
        #     size_down = max_size
        #
        # font_down = ImageFont.truetype('fonts/timesnewromanpsmt.ttf', size=size_down)

        # Определите максимальную ширину текста и разделите текст на несколько строк
        max_width = 40
        lines_down = textwrap.wrap(text__demotivator_down, width=max_width)

        max_size = 1 / 10 * height
        max_len_down = max(len(line) for line in lines_down)

        size = int((width * 0.9) / max(len(line) for line in lines_down) / 0.6)
        if size > max_size:
            size = max_size

        font_down = ImageFont.truetype('fonts/timesnewromanpsmt.ttf', size=size)
        for line in lines_down:
            if len(line) == max_len_down:
                max_linen_down = line
                break

        w_text = font_down.getmask(max_linen_down).getbbox()[2]
        while w_text > 0.8 * width:
            size -= 0.01 * size
            font_down = ImageFont.truetype('fonts/timesnewromanpsmt.ttf', size=size)
            w_text = font_down.getmask(max_linen_down).getbbox()[2]

        line_height_down = sum(font_down.getmetrics())

    else:
        line_height_down = 0
        lines_down = []

    # Создание черной рамки вокруг изображения
    border = (int(0.06 * width),
              int(0.06 * height),
              int(0.06 * width),
              len(lines_down) * line_height_down + len(lines_up) * line_height_up + 2 * int(
                  height * 0.05))  # Левая, верхняя, правая и нижняя границы

    pic = ImageOps.expand(pic, border, fill='black')

    draw = ImageDraw.Draw(pic)

    draw.rectangle([(int(0.05 * width),
                     int(0.05 * height)),
                    (width + border[0] + border[2] - int(0.05 * width),
                     height + border[1] + int(0.01 * height))], outline='white', width=4)  # толщина рамки)

    # Начальная координата так, чтобы текст всегда был на одинаковом расстоянии от нижнего края изображения
    y1 = height + border[1] + int(height * 0.04)

    for lineu in lines_up:
        w_text = font_up.getmask(lineu).getbbox()[2]
        x = (width - w_text) // 2 + border[0]
        draw.text((x, y1), lineu, fill='white', font=font_up)

        # Переход к следующей строке
        y1 += line_height_up

    # Начальная координата так, чтобы текст всегда был на одинаковом расстоянии от нижнего края изображения
    y2 = height + border[1] + border[3] - int(height * 0.04) - len(lines_down) * line_height_down

    for line in lines_down:
        w_text = font_down.getmask(line).getbbox()[2]
        x = (width - w_text) // 2 + border[0]
        draw.text((x, y2), line, fill='white', font=font_down)

        # Переход к следующей строке
        y2 += line_height_down

    os.remove(pic_name)
    pic.save(pic_name, quality=95)

    return pic_name  # возвращает адрес к пикче, а не саму пикчу
