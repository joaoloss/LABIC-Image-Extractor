import matplotlib.pyplot as plt
import numpy as np
import os
from tqdm import tqdm
from argparse import ArgumentParser
import subprocess
from dotenv import load_dotenv

from pathlib import Path
import json
import cv2

def get_json_files(ip, token):
    url_crisis = f"http://{ip}:7777/api/projects/7/export?exportType=JSON&download_all_tasks=true"
    url_users = f"http://{ip}:7777/api/users/"
    headers = f"-H 'Authorization: Token {token}' -H 'Accept: application/json'"

    _command_output_crisis = f"curl -X GET '{url_crisis}' {headers} -o output_crisis.json"
    _command_get_users = f"curl -X GET '{url_users}' -H 'Authorization: Token {token}' -o users.json"
    
    subprocess.run(_command_output_crisis, shell=True)
    subprocess.run(_command_get_users, shell=True)

def parse_args():
    parser = ArgumentParser()
    
    parser.add_argument(
        "-v", "--verbose",
        choices=[0, 1, 2],
        default=0,
        help="Set verbosity level: 0 (silent), 1 (normal), 2 (debug)"
    )
    parser.add_argument(
        "-gj", "--get-json",
        action="store_true",
        help="Get json files from Label Studio flag. If not set no requisition is made"
    )
    parser.add_argument(
        "-ip",
        default="10.147.17.142",
        help="Set the ip to get the json files"
    )
    
    args = parser.parse_args()
    
    return args

def create_dir(path, verbose):
    os.makedirs(path, exist_ok=True)
    
    if verbose:
        print(path)

def analyse_json_path(path_json, path_obj, verbose):
    if '.' not in path_json:
        if verbose: 
            print("Recurso técnico")
        for file in Path(path_obj.parents[0]).glob(path_obj.parts[-1] + "*"):
            path_json = file.as_posix()
    
    if verbose:
        print(path_json)
    
    return path_json

def main():
    load_dotenv()
    args = parse_args()
    
    verbose = args.verbose
    get_json_flag = args.get_json
    ip = args.ip
    
    token = os.getenv("TOKEN")
    
    if get_json_flag:
        print("Getting json files...")
        get_json_files(ip, token)
        
    with open("users.json", encoding="utf-8") as f:
        users = json.load(f)
    
    with open('output_crisis.json', encoding='utf-8') as f:
        labels = json.load(f)
    
    id_to_name = {}
    
    for user in users:
        id_to_name[user["id"]] = user["username"].replace(".", "_")

    output_folder = "output"
    create_dir(output_folder, verbose=verbose)        
    count = 0
    with tqdm(total=len(labels), desc="Labels: ", unit="label") as pb:
        for label in labels:
            path_json = label["data"]["path_destino"]
            path_obj = Path(path_json)
            
            path_json = analyse_json_path(path_json, path_obj, verbose)
            
            img = cv2.imread(path_json, cv2.IMREAD_COLOR)
            
            if img is not None:
                RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                dim = np.shape(RGB_img)
                if verbose:
                    print("Dimensions",dim)
                        
                if verbose >= 2:
                    plt.imshow(RGB_img)
                    plt.title('Image', fontsize = 14, fontweight ='bold')
                    plt.axis('off')
                    plt.show()

                annotations_list = label["annotations"]
                for annotations in annotations_list:
                    completed_by_name = id_to_name[int(annotations["completed_by"])]
                    results = annotations['result']

                    create_dir(os.path.join(output_folder, completed_by_name), verbose=verbose)
                    for i in range(0, len(results)):
                        value = results[i]["value"]
                        if verbose:
                            print("i:",i)
                            print("annotation:",value)
                        
                        
                        if len(value.keys()) >= 2:
                            label = value["rectanglelabels"][0]
                            
                            if "Não" in label:
                                label = label.replace("Não","Nao")
                            if ' ' in label:
                                label = label.replace(" ","_")
                            
                            create_dir(os.path.join(output_folder, completed_by_name, label), verbose)
                            image_path_ = Path(output_folder, completed_by_name, label, completed_by_name + '_' + path_obj.parts[1] + "_" + str(i) + "_" + path_obj.parts[2])


                            
                            if verbose:
                                print(path_obj.parts[1:])
                                print("image_path_:",image_path_)
                                print("label:",label)
                            
                            y = int(float(value["x"])*dim[0]/100)
                            x = int(float(value["y"])*dim[1]/100)
                            height = int(float(value["height"])*dim[0]/100)
                            width = int(float(value["width"])*dim[1]/100)
                            
                            if verbose:
                                print(x,y,height,width)
                            
                            RGB_ = RGB_img[x:x+height, y:y+width]
                            BGR_ = img[x:x+height, y:y+width]
                            
                            if verbose:
                                print("Dim crop:",np.shape(RGB_))
                            
                            if np.shape(RGB_)[0] >= 2 and np.shape(RGB_)[1] >= 2:
                                if verbose >= 2:
                                    plt.imshow(RGB_)
                                    plt.title('Crop Image', fontsize = 14, fontweight ='bold')
                                    plt.axis('off')
                                    plt.show()
                                    
                                if '.' not in image_path_.as_posix():
                                    image_path_ = Path(image_path_.as_posix() + ".jpg")
                                try:
                                    cv2.imwrite(image_path_.as_posix(), BGR_)
                                except cv2.error:
                                    print(image_path_)
                                    exit(1)
                    
                    count += 1
                    
                if verbose:
                    print(f"Processed:{count}")
            
            pb.update()
        

if __name__ == "__main__":
    main()