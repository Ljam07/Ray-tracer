import glm
from PIL import Image
import math
import sys
from Sphere import Sphere, Material, Light

def refract(I: glm.vec3, N: glm.vec3, RI: float) -> glm.vec3:
    # Ensure input vectors are normalized
    I = glm.normalize(I)
    N = glm.normalize(N)

    # Compute the cosine of the angle of incidence
    cosi = max(-1.0, min(1.0, glm.dot(I, N)))
    etai = 1.0
    etat = RI
    n = N

    # Adjust the normal and indices of refraction based on the incident direction
    if cosi < 0:
        cosi = -cosi
    else:
        etai, etat = etat, etai
        n = -N

    eta = etai / etat
    k = 1.0 - eta * eta * (1.0 - cosi * cosi)

    # Handle total internal reflection
    if k < 0.0:
        return glm.vec3(0.0, 0.0, 0.0)  # Total internal reflection, no refraction

    # Compute the refracted direction
    refracted_dir = eta * I + (eta * cosi - glm.sqrt(k)) * n
    return glm.normalize(refracted_dir)



def reflect(I, N):
    # Normalize the input vectors to avoid issues with zero-length vectors
    I = glm.normalize(I)
    N = glm.normalize(N)
    
    # Handle edge case where dot product is negative or zero
    dot_product = glm.dot(I, N)
    if abs(dot_product) < 1e-6:  # Very small values close to zero
        return I  # If nearly perpendicular, return the incident vector (no reflection)
    
    return I - N * 2.0 * dot_product


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



def cast_ray(orig, dir, spheres, lights, depth=0):
    if depth > 4:
        # Maximum recursion depth to prevent infinite reflection
        return glm.vec3(0.2, 0.7, 0.8)  # Background colour

    # Check for intersection with the scene
    hit, normal, material, _ = scene_intersect(orig, dir, spheres)
    
    if hit is None:
        return glm.vec3(0.2, 0.7, 0.8)  # Background colour if no hit


    # Reflection handling
    reflect_dir = glm.normalize(reflect(dir, normal))
    refract_dir = glm.normalize(refract(dir, normal, material.refractive_index))
    # if glm.dot(reflect_dir, normal) < 0:
    #     print("Warning: Reflection direction invalid!")

    reflect_orig = hit + normal * 1e-3 if glm.dot(reflect_dir, normal) > 0 else hit - normal * 1e-3
    refract_orig = hit + normal * 1e-3 if glm.dot(refract_dir, normal) > 0 else hit - normal * 1e-3
    reflect_color = cast_ray(reflect_orig, reflect_dir, spheres, lights, depth + 1)
    refract_color = cast_ray(refract_orig, refract_dir, spheres, lights, depth + 1)

    # Lighting calculations
    diffuse_light_intensity = 0.0
    specular_light_intensity = 0.0

    for light in lights:
        light_dir = glm.normalize(light.position - hit)
        light_distance = glm.length(light.position - hit)

        # Shadow ray
        shadow_orig = hit + normal * 1e-3 if glm.dot(light_dir, normal) > 0 else hit - normal * 1e-3
        shadow_hit, _, _, _ = scene_intersect(shadow_orig, light_dir, spheres)
        
        # Check if the shadow point is closer than the light source
        if shadow_hit is not None and glm.length(shadow_hit - shadow_orig) < light_distance:
            continue  # Point is in shadow, skip light contribution

        # Diffuse component (Lambertian reflection)
        diffuse_light_intensity += light.intensity * max(0.0, glm.dot(light_dir, normal))

        # Specular component (Blinn-Phong reflection)
        halfway_dir = glm.normalize(light_dir - dir)  # Halfway vector
        specular_light_intensity += (
            pow(max(0.0, glm.dot(halfway_dir, normal)), material.specular_exponent) * light.intensity
        )

    # Final colour calculation
    colour = (
        material.diffuse_color * diffuse_light_intensity * material.albedo.x +  # Diffuse
        glm.vec3(1, 1, 1) * specular_light_intensity * material.albedo.y +     # Specular
        reflect_color * material.albedo.z + refract_color*material.albedo.w    # Reflection
    )
    return glm.clamp(colour, 0.0, 1.0)  # Ensure the colour is within valid range




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

    ivory = Material(1.0, glm.vec4(0.6, 0.3, 0.1, 0.0), glm.vec3(0.4, 0.4, 0.3), 50)  
    glass = Material(1.5, glm.vec4(0.0, 0.5, 0.1, 0.8), glm.vec3(0.6, 0.7, 0.8), 125)  
    red_rubber = Material(1.0, glm.vec4(0.9, 0.1, 0.0, 0.0), glm.vec3(0.3, 0.1, 0.1), 10)
    mirror = Material(1.0, glm.vec4(0.0, 10.0, 0.8, 0.0), glm.vec3(1.0, 1.0, 1.0), 1425) 


    spheres = [
    Sphere(glm.vec3(-3, 0, -16), 2, ivory),
    Sphere(glm.vec3(-1.0, -1.5, -12), 2, glass),
    Sphere(glm.vec3(1.5, -0.5, -18), 3, red_rubber),
    Sphere(glm.vec3(7, 5, -18), 4, mirror)
]


    light = Light(glm.vec3(-20, 20, 20), 1.5)
    light2 = Light(glm.vec3(30, 50, -25), 1.8)
    light3 = Light(glm.vec3(30, 20, 30), 1.7)

    lights = [light, light2, light3]
    #lights = [light]

    framebuffer = generate_colors(width, height, spheres, lights)
    img = create_image_from_colors(framebuffer)
    save_image(img, output_file)

if __name__ == "__main__":
    width = 1920
    heigt = 1080
    render(width=1024, height=768, output_file="output.png")
