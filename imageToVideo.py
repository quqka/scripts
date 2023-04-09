import os, sys, re
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import imageio
import rtoml

config = {
    "image_type": [".jpg", ".png"],
    "fps": 30,
#    "output": "output",
    "quality": 10,
    "codec": "libx264",
    "max_workers":5
}
video_type = {
    "msmpeg4": ".wmv",
    "libx264": ".mp4"
}

def image_to_video(image_dir, output_path, image_files):
    if len(image_files) == 0:
        return
#    if not os.path.exists(output_path):
#        os.mkdir(output_path)
    with ThreadPoolExecutor(max_workers=config["max_workers"]) as executor:
        images = list(tqdm(executor.map(imageio.imread, image_files), total=len(
            image_files), desc=f"{image_dir} Images Processing"))

    image_dir = os.path.normpath(image_dir)
    filename = re.split("\\\|\:|\/",image_dir)[-1] + output_path + video_type[config['codec']]
    filepath = os.path.join(os.path.abspath(os.path.join(image_dir, "..")), filename)
#    filename = '_'.join(re.split("\\\|\:|\/",image_dir)) + video_type[config['codec']]

    count = 0
    with imageio.get_writer(filepath, fps=config["fps"], quality=config["quality"], codec=config["codec"]) as video:
        for image in images:
            print("\rGenerating {}".format("."*(count % 4)), end="", flush=True)
            video.append_data(image)
            count += 1
    print(f"\r\033[32mSuccessfully generated {filepath} !!!\033[0m")

def main():
    data = sys.argv[1:]
    if len(data) == 0:
        return
    if os.path.exists("imageToVideo.toml"):
        try:
            config.update(rtoml.load(open("imageToVideo.toml")))
        except:
            pass
    work_dict = {}

    for i in data:
        if os.path.isdir(i):
            for it in config["image_type"]:
                if i not in work_dict:
                    work_dict[i] = {}
                work_dict[i][it] = list(filter(lambda file: file.endswith(
                    it), [os.path.join(i, file) for file in os.listdir(i)]))
        elif os.path.isfile(i):
            for it in config["image_type"]:
                if i.endswith(it):
                    dir = os.path.dirname(i)
                    if dir not in work_dict:
                        work_dict[dir] = {}
                    if it not in work_dict[dir]:
                        work_dict[dir][it] = []
                    work_dict[dir][it].append(i)

#    output_path = config["output"]
#    if not os.path.exists(output_path):
#        os.mkdir(output_path)

    for key, value in work_dict.items():
        for i, j in value.items():
            image_to_video(key, i, sorted(j))
#            image_to_video(key, output_path if len(value) == 0 else os.path.join(output_path, i.lstrip(".")), sorted(j))


if __name__ == "__main__":
    main()
