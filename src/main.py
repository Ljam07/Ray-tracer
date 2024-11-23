import glm
from PIL import Image
import math
import sys
from Sphere import Sphere, Material, Light

def reflect(I, N):
    return I - N * 2.0 * (I * N)

def scene_intersect(orig, dir, spheres):
    closest_dist = sys.float_info.max
    hit = None
    normal = None
    material = None
    color = glm.vec3(0.2, 0.7, 0.8)

    for sphere in spheres:
        t0 = sphere.ray_intersect(orig, dir)
        
        if t0 is not None and t0 < closest_dist:
            closest_dist = t0
            hit = orig + dir * t0
            normal = glm.normalize(hit - sphere.center)
            material = sphere.material
            color = material.diffuse_color
    
    return hit, normal, material, color



def cast_ray(orig, dir, spheres, lights):
    hit, normal, material, color = scene_intersect(orig, dir, spheres)

    if hit is None:
        return glm.vec3(0.2, 0.7, 0.8)

    diffuse_intensity = 0
    specular_light_intensity = 0

    for light in lights:
        light_dir = glm.normalize(light.position - hit)
        diffuse_intensity += light.intensity * max(0, glm.dot(normal, light_dir))
        
        reflection = reflect(-light_dir, normal)
        specular_light_intensity += pow(max(0, glm.dot(reflection, -dir)), material.specular_exponent) * light.intensity


    return (
    color * diffuse_intensity * material.albedo.x +  # Use the diffuse component of albedo
    glm.vec3(1, 1, 1) * specular_light_intensity * material.albedo.y  # Use the specular component of albedo
)



def generate_colors(width, height, spheres, lights):
    """
    Generate a framebuffer of colors using glm.vec3.
    Each pixel's color is a gradient based on its position.

    Args:
    - width: Width of the image.
    - height: Height of the image.

    Returns:
    - A 2D list of glm.vec3 representing the image's colors.
    """
    fov = math.pi/2
    framebuffer = []
    for j in range(height):
        row = []
        for i in range(width):
            # Gradient from top (red) to bottom (green), no blue.
            x = (2*(i+0.5)/float(width) - 1) * glm.tan(fov/2.0) * width / float(height)
            y = -(2*(j + 0.5)/float(height) - 1)*glm.tan(fov/2)
            dir = glm.normalize(glm.vec3(x, y, -1))
            color = cast_ray(glm.vec3(0, 0, 0), dir, spheres, lights)
            row.append(color)
        framebuffer.append(row)
    return framebuffer


def create_image_from_colors(framebuffer):
    """
    Convert the framebuffer (2D list of glm.vec3 colors) into a Pillow Image object.

    Args:
    - framebuffer: 2D list of glm.vec3 objects containing color data.

    Returns:
    - A Pillow Image object.
    """
    height = len(framebuffer)
    width = len(framebuffer[0])
    img = Image.new("RGB", (width, height))

    # Convert framebuffer colors to RGB and set pixels in the image
    for j in range(height):
        for i in range(width):
            r = int(255 * glm.clamp(framebuffer[j][i].x, 0.0, 1.0))
            g = int(255 * glm.clamp(framebuffer[j][i].y, 0.0, 1.0))
            b = int(255 * glm.clamp(framebuffer[j][i].z, 0.0, 1.0))
            img.putpixel((i, j), (r, g, b))

    return img


def save_image(img, file_path):
    """
    Save the Pillow Image object to a file.

    Args:
    - img: The Pillow Image object to save.
    - file_path: The path (including filename and extension) where the image should be saved.
    """
    img.save(file_path)
    print(f"Image saved to {file_path}")


def render(width=1024, height=768, output_file="output.png"):
    """
    Main render function that generates an image and saves it.

    Args:
    - width: Width of the output image.
    - height: Height of the output image.
    - output_file: File path to save the output image.
    """

    ivory = Material(glm.vec2(0.6, 0.3), glm.vec3(0.4, 0.4, 0.3), 50)
    red_rubber = Material(glm.vec2(0.9, 0.1), glm.vec3(0.3, 0.1, 0.1), 10)

    spheres = [
    Sphere(glm.vec3(-3, 0, -16), 2, ivory),
    Sphere(glm.vec3(-1.0, -1.5, -12), 2, red_rubber),
    Sphere(glm.vec3(1.5, -0.5, -18), 3, red_rubber),
    Sphere(glm.vec3(7, 5, -18), 4, ivory)
]


    light = Light(glm.vec3(20, 20, 20), 1.5)
    light2 = Light(glm.vec3(30, 50, -25), 1.8)
    light3 = Light(glm.vec3(30, 20, 30), 1.7)

    lights = [light, light2, light3]
    #lights = [light]

    framebuffer = generate_colors(width, height, spheres, lights)
    img = create_image_from_colors(framebuffer)
    save_image(img, output_file)



if __name__ == "__main__":
    render(width=1024, height=768, output_file="output.png")
