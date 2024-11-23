import glm
from PIL import Image
from Sphere import Sphere  # Import the Sphere class correctly

def cast_ray(orig: glm.vec3, dir: glm.vec3, sphere: Sphere):
    t0 = sphere.ray_intersect(orig, dir)
    if t0 is None:
        return glm.vec3(0.2, 0.7, 0.8)  # Background color (sky-blue)
    return glm.vec3(0.4, 0.4, 0.3)  # Color of the sphere

def generate_colors(width, height, sphere: Sphere):
    fov = 90  # Field of view
    framebuffer = []
    
    for j in range(height):
        row = []
        for i in range(width):
            x = (2 * (i + 0.5) / float(width) - 1) * glm.tan(fov / 2) * width / float(height)
            y = -(2 * (j + 0.5) / float(height) - 1) * glm.tan(fov / 2)
            dir = glm.normalize(glm.vec3(x, y, -1))  # Ray direction
            
            color = cast_ray(glm.vec3(0, 0, 0), dir, sphere)
            row.append(color)
        framebuffer.append(row)
        if round((j / height) * 100) % 10 == 0:
            print(f"{round((j / height) * 100)}% done")

    
    return framebuffer

def create_image_from_colors(framebuffer):
    height = len(framebuffer)
    width = len(framebuffer[0])
    img = Image.new("RGB", (width, height))

    for j in range(height):
        for i in range(width):
            r = int(255 * glm.clamp(framebuffer[j][i].x, 0.0, 1.0))
            g = int(255 * glm.clamp(framebuffer[j][i].y, 0.0, 1.0))
            b = int(255 * glm.clamp(framebuffer[j][i].z, 0.0, 1.0))
            img.putpixel((i, j), (r, g, b))

    return img

def save_image(img, file_path):
    img.save(file_path)
    print(f"Image saved to {file_path}")

def render(width=1024, height=768, output_file="output.png"):
    # Create the sphere object correctly
    sphere = Sphere(glm.vec3(-3, 0, -16), 2)  # Sphere at position (-3, 0, -16) with radius 2
    framebuffer = generate_colors(width, height, sphere)
    img = create_image_from_colors(framebuffer)
    save_image(img, output_file)

if __name__ == "__main__":
    render(width=1024, height=768, output_file="output.png")
