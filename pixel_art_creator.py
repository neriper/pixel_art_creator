import os
import argparse
from PIL import Image

def create_pixel_art(input_img, input_palette, pixel_size, output_size):
    """
    Преобразует исходное изображение в pixel art с использованием заданной палитры
    Краткий алгоритм:
        - берется изображение input_img
        - разбивается на блоки по pixel_size
        - в каждом блоке находится преобладающий цвет
        - преобладающий цвет сопоставляется с палитрой input_palette
        - на весь блок ставится выбранный цвет палитры
        - полученное изображение маштабируется под размер output_size на output_size

    Параметры:
        input_img (str): путь к исходному изображению (.png, .jpeg, .jpg)
        input_palette (str): путь к изображению-палитре (полоска высотой 1 пиксель)
        pixel_size (int): размер квадратной области для анализа (в пикселях исходника)
        output_size (int): размер итогового квадратного изображения (в пикселях)
    """
    # загрузка изображения с сохранением альфа-канала
    try:
        img = Image.open(input_img).convert('RGBA')
    except Exception as e:
        print(f"Ошибка при открытии исходного изображения: {e}")
        return

    # загрузка палитры
    try:
        palette_img = Image.open(input_palette).convert('RGB')
    except Exception as e:
        print(f"Ошибка при открытии палитры: {e}")
        return

    # извлесение цвето из палитры (только RGB)
    palette_colors = []
    w, h = palette_img.size
    if h != 1:
        print("Предупреждение: палитра имеет высоту не 1px. Будет использована первая строка.")
    for x in range(w):
        color = palette_img.getpixel((x, 0))
        if color not in palette_colors:
            palette_colors.append(color)

    if not palette_colors:
        print("Палитра не содержит цветов.")
        return

    # дробление исходного изображения на блоки по заданному размеру pixel_size
    width, height = img.size
    cols = width // pixel_size
    rows = height // pixel_size
    if cols == 0 or rows == 0:
        print("pixel_size слишком велик для данного изображения.")
        return

    # создание промежуточного изображение с альфа-каналом
    block_img = Image.new('RGBA', (cols, rows))

    # обработка каждого блока исходного изображения
    for i in range(rows):
        for j in range(cols):
            left = j * pixel_size
            top = i * pixel_size
            right = left + pixel_size
            bottom = top + pixel_size
            block = img.crop((left, top, right, bottom))

            # Получаем все пиксели блока (RGBA)
            pixels = list(block.getdata())

            # Проверяем, есть ли непрозрачные пиксели
            opaque_pixels = [(r, g, b) for r, g, b, a in pixels if a > 0]
            if not opaque_pixels:
                # Блок полностью прозрачен – ставим прозрачный пиксель
                block_img.putpixel((j, i), (0, 0, 0, 0))
                continue

            # Вычисляем средний цвет только по непрозрачным пикселям
            total_r = total_g = total_b = 0
            for r, g, b in opaque_pixels:
                total_r += r
                total_g += g
                total_b += b
            num_opaque = len(opaque_pixels)
            avg_r = total_r // num_opaque
            avg_g = total_g // num_opaque
            avg_b = total_b // num_opaque

            # Поиск ближайшего цвета в палитре (евклидово расстояние по RGB)
            min_dist = float('inf')
            best_color = palette_colors[0]
            for pr, pg, pb in palette_colors:
                dr = avg_r - pr
                dg = avg_g - pg
                db = avg_b - pb
                dist = dr*dr + dg*dg + db*db
                if dist < min_dist:
                    min_dist = dist
                    best_color = (pr, pg, pb)

            # Записываем выбранный цвет (полностью непрозрачный) в промежуточное изображение
            block_img.putpixel((j, i), (*best_color, 255))

    # маштабирования изображения до требуемого размера (без сглаживания, сохраняя альфу)
    final_img = block_img.resize((output_size, output_size), Image.NEAREST)

    # Сохранение результата рядом с исходным файлом в формате PNG (поддерживает прозрачность)
    base, ext = os.path.splitext(input_img)
    output_path = base + "_pixel_art.png"
    final_img.save(output_path)
    print(f"Изображение сохранено как {output_path}")


if __name__ == "__main__":
    # create_pixel_art(
    #     input_img="test_data/test_image.png",
    #     input_palette="test_data/test_palette.png",
    #     pixel_size=1,
    #     output_size=32
    # )

    parser = argparse.ArgumentParser(description='Создание пиксель-арта из изображения')
    parser.add_argument('input_img', help='Путь к входному изображению')
    parser.add_argument('input_palette', help='Путь к файлу с палитрой')
    parser.add_argument('pixel_size', type=int, help='Размер пикселя')
    parser.add_argument('output_size', type=int, help='Размер выходного изображения')

    args = parser.parse_args()

    create_pixel_art(
        args.input_img,
        args.input_palette,
        args.pixel_size,
        args.output_size
    )