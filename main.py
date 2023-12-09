import pyautogui
from PIL import Image, ImageChops, ImageFilter, ImageOps
import time

text_image_path = 'you_died.png'
death_count_file = 'death_count.txt'

death_count = 0


def is_death_text_present(text_image: Image, screenshot: Image, mask_image: Image):
    text_image = text_image.convert("RGBA")
    mask_image = mask_image.convert("RGBA")
    global death_count

    mask = text_image.split()[3]

    if mask:
        bbox = mask.getbbox()
        if bbox:
            screenshot_crop = screenshot.crop(bbox)
            text_image_crop = text_image.crop(bbox)
            mask_image_crop = mask_image.crop(bbox)

            maskNew = mask_image_crop.convert('L')
            maskNew = ImageOps.invert(maskNew).filter(ImageFilter.GaussianBlur(0.5))
            maskNew = ImageChops.screen(maskNew, maskNew)

            screenshot_crop = screenshot_crop.convert("RGB")
            text_image_crop = text_image_crop.convert("RGB")

            gaussianLow = 0.3
            gaussianHigh = gaussianLow + 0.3

            sstEdges = ImageOps.autocontrast(
                ImageChops.difference(screenshot_crop.split()[0]
                                      .filter(ImageFilter.GaussianBlur(gaussianLow)),
                                      screenshot_crop.split()[0]
                                      .filter(ImageFilter.GaussianBlur(gaussianHigh))))
            txtEdges = ImageOps.autocontrast(
                ImageChops.difference(text_image_crop.split()[0]
                                      .filter(ImageFilter.GaussianBlur(gaussianLow)),
                                      text_image_crop.split()[0]
                                      .filter(ImageFilter.GaussianBlur(gaussianHigh))))

            sstEdges = ImageOps.autocontrast(sstEdges.filter(ImageFilter.SMOOTH))
            txtEdges = ImageOps.autocontrast(txtEdges.filter(ImageFilter.SMOOTH))

            sstEdges = ImageChops.add(sstEdges, sstEdges).filter(ImageFilter.SMOOTH)
            txtEdges = ImageChops.add(txtEdges, txtEdges).filter(ImageFilter.SMOOTH)

            diffEdge = ImageChops.difference(sstEdges, txtEdges)

            screenshot_crop = ImageChops.multiply(screenshot_crop, screenshot_crop)
            text_image_crop = ImageChops.multiply(text_image_crop, text_image_crop)
            screenshot_crop = ImageOps.autocontrast(screenshot_crop)
            text_image_crop = ImageOps.autocontrast(text_image_crop)
            diffColor = ImageChops.difference(screenshot_crop, text_image_crop).filter(ImageFilter.GaussianBlur(1))

            diffColor = diffColor.convert("RGB")
            diffColor.putalpha(255)
            diffColor.paste((0, 0, 0), maskNew)
            maskWidth, maskHeight = maskNew.size
            colorMaskBlackPercentage = 0

            for y in range(maskHeight):
                for x in range(maskWidth):
                    pixel_value = maskNew.getpixel((x, y))
                    colorMaskBlackPercentage += 1 - (pixel_value / 255)

            colorMaskBlackPercentage = (colorMaskBlackPercentage / (maskWidth * maskHeight)) * 100

            maskNew = maskNew.filter(ImageFilter.GaussianBlur(3))
            maskNew = ImageChops.multiply(maskNew, maskNew)
            maskNew = ImageChops.multiply(maskNew, maskNew)

            diffEdge = diffEdge.convert("RGB")
            diffEdge.paste((0, 0, 0), maskNew)
            diffEdgeChannelR = diffEdge.split()[0]
            edgeMaskBlackPercentage = 0

            for y in range(maskHeight):
                for x in range(maskWidth):
                    pixel_value = maskNew.getpixel((x, y))
                    edgeMaskBlackPercentage += 1 - (pixel_value / 255)

            edgeMaskBlackPercentage = (edgeMaskBlackPercentage / (maskWidth * maskHeight)) * 100

            diffEdgeChannelR.save("gui/diffEdge.png", "PNG")
            diffColor.save("gui/diffColor.png", "PNG")

            diff_array_edge = list(diffEdgeChannelR.getdata())
            avg_diff_edge = (sum(diff_array_edge) / len(diff_array_edge))

            diff_array_color_R = list(diffColor.split()[0].getdata())
            diff_array_color_G = list(diffColor.split()[1].getdata())
            diff_array_color_B = list(diffColor.split()[2].getdata())
            avg_diff_color = ((sum(diff_array_color_R) + sum(diff_array_color_G) + sum(diff_array_color_B)) /
                              (len(diff_array_color_R) + len(diff_array_color_G) + len(diff_array_color_B)))

            avg_diff_edge /= 255
            avg_diff_color /= 255
            avg_diff_edge = (((100 - (
                round(avg_diff_edge * 100000)) / 1000) - edgeMaskBlackPercentage) / (
                        100 - edgeMaskBlackPercentage)) * 100
            avg_diff_color = (((100 - (
                round(avg_diff_color * 100000)) / 1000) - colorMaskBlackPercentage) / (
                                                100 - colorMaskBlackPercentage)) * 100

            (open('gui/data.txt', 'w')
             .write(f"{death_count}\n{avg_diff_edge}\n{avg_diff_color}"))
            return (avg_diff_edge > 90) & (avg_diff_color > 87)
        return False


def read_death_count():
    global death_count
    try:
        with open(death_count_file, 'r') as file:
            death_count = int(file.read())
    except FileNotFoundError:
        death_count = 0
    return death_count


def write_death_count(count):
    with open(death_count_file, 'w') as file:
        file.write(str(count))


def main():
    global death_count
    global death_count
    txt_img = Image.open(text_image_path)
    msk_img = Image.open('mask.png')

    death_count = read_death_count()

    while True:
        scrsht = pyautogui.screenshot()

        if is_death_text_present(txt_img, scrsht, msk_img):
            death_count += 1
            write_death_count(death_count)
        time.sleep(0.05)


if __name__ == "__main__":
    main()
