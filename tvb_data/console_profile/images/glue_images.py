
import Image

WIDTH = 1550
HEIGHT = 985
GLUE_DEFINITION = [{"suffix": "RI", "position": (0, 0)},
                   {"suffix": "LI", "position": (WIDTH, 0)},
                   {"suffix": "RO", "position": (0, HEIGHT)},
                   {"suffix": "LO", "position": (WIDTH, HEIGHT)}]
BRANDING_BAR_PATH = "../framework_tvb/tvb/core/services/resources/branding_bar.png"



def glue_4_images(path_prefix):

    final_image = Image.new("RGBA", (2 * WIDTH, 2 * HEIGHT))

    for i in xrange(4):
        image_path = path_prefix + "_" + GLUE_DEFINITION[i]["suffix"] + ".png"
        img = Image.open(image_path)
        final_image.paste(img, GLUE_DEFINITION[i]["position"], img)

    branding_bar = Image.open(BRANDING_BAR_PATH)
    final_image.paste(branding_bar, (0, final_image.size[1] - branding_bar.size[1]), branding_bar)

    final_path = path_prefix + ".png"
    final_path = final_path.replace("ExportedRaw", "Glued")
    final_image.save(final_path, "PNG")

    print "Saved image:", final_path



def glue_6_images(path_prefix):

    final_image = Image.new("RGBA", (2 * WIDTH, 12 * HEIGHT))

    for i in range(1, 7):
        image_path = path_prefix + str(i) + ".png"
        img = Image.open(image_path)
        final_image.paste(img, (0, (i - 1) * 2 * HEIGHT), img)

    branding_bar = Image.open(BRANDING_BAR_PATH)
    final_image.paste(branding_bar, (0, final_image.size[1] - branding_bar.size[1]), branding_bar)

    final_path = path_prefix + "Group.png"
    final_image.save(final_path, "PNG")

    print "Saved image:", final_path


def glue_2_images(image1, image2, final_path):

    final_image = Image.new("RGB", (4 * WIDTH, 12 * HEIGHT))

    img = Image.open(image1)
    final_image.paste(img, (0, 0), img)
    img = Image.open(image2)
    final_image.paste(img, (2 * WIDTH, 0), img)

    branding_bar = Image.open(BRANDING_BAR_PATH)
    final_image.paste(branding_bar, (0, final_image.size[1] - branding_bar.size[1]), branding_bar)

    final_image.save(final_path, "PNG")
    print "Saved image:", final_path


if __name__ == "__main__":

    for i in range(1, 7):
        glue_4_images("/Users/lia.domide/Downloads/Mantini/Images_ExportedRaw_Empiric/MantiniNet" + str(i))

    #glue_6_images("/Users/lia.domide/Downloads/Mantini/Images_Glued_Empiric/MantiniNet")

    for i in range(1, 7):
        glue_4_images("/Users/lia.domide/Downloads/Mantini/Images_ExportedRaw_Simulation/Measure" + str(i))

    #glue_6_images("/Users/lia.domide/Downloads/Mantini/Images_Glued_Simulation/Measure")

    #glue_2_images("/Users/lia.domide/Downloads/Mantini/Images_Glued_Empiric/MantiniNetGroup.png",
    #              "/Users/lia.domide/Downloads/Mantini/Images_Glued_Simulation/MeasureGroup.png",
    #              "/Users/lia.domide/Downloads/Mantini/Mantini.png")
