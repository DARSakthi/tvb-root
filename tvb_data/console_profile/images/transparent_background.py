
import os
import Image



def process_image(image_path, result_path, discrepancy):
    img = Image.open(image_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if 255 - item[0] < discrepancy and 255 - item[1] < discrepancy and 255 - item[2] < discrepancy:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(result_path, "PNG")



def process_folder(root_folder, discrepancy):

    count = 0
    for dir_path, _, file_names in os.walk(root_folder):
        for file_name in file_names:
            if file_name.endswith("png") and "_tr.png" not in file_name:
                original_png_path = os.path.join(dir_path, file_name)
                result_png_path = original_png_path.replace(".png", "_tr.png")
                process_image(original_png_path, result_png_path, discrepancy)
                count += 1
    print str(count) + " images were transformed in folder " + root_folder



if __name__ == "__main__":

    #process_folder("brain-collage/hotcold-connectivity", 10)
    #process_folder("brain-collage/hotcold-persp", 10)
    #process_folder("brain-collage/hotcold-side", 10)

    #process_folder("brain-collage/tvb-side", 10)
    #process_folder("brain-collage/tvb-top", 10)
    process_folder("brain-collage/tvb-persp", 10)
