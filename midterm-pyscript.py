cv2_image = cv2.cvtColor(np.array(cam.raw_image), cv2.COLOR_RGB2HSV)
cv2_image_RGB = cv2.cvtColor(cv2_image, cv2.COLOR_HSV2RGB)
display(Image.fromarray(cv2_image_RGB))

colors = ["red", "green"]
mag = 15
lower_bound = 70
color_one_count = 0
color_two_count = 0
for color in colors:
    if color == "red":
        lower_red1 = np.array([0, lower_bound, lower_bound])
        upper_red1 = np.array([0 + mag, 255, 255])
        lower_red2 = np.array([180 - mag, lower_bound, lower_bound])
        upper_red2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(cv2_image, lower_red1, upper_red1)
        mask2 = cv2.inRange(cv2_image, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
    if color == "green":
        lower = np.array([60 - mag*2, lower_bound-10, lower_bound-10])
        upper = np.array([60 + mag*2, 255, 255])
        mask = cv2.inRange(cv2_image, lower, upper)

    kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype=np.uint8)
    # display(Image.fromarray(mask))

    eroded = cv2.erode(mask, kernel)
    # display(Image.fromarray(eroded))
    dilated = cv2.dilate(eroded, kernel)
    # display(Image.fromarray(dilated))

    masked = cv2.bitwise_and(cv2_image_RGB, cv2_image_RGB, mask=dilated)
    display(Image.fromarray(masked))
    count = np.count_nonzero(dilated)
    # print(count)
    if color == "red":
        color_one_count = count
    else:
        color_two_count = count

new_val = "F" if color_one_count > color_two_count else "C"
print(f"updating airtable... to {new_val}")
from pyodide.http import pyfetch
import json
import asyncio


async def patch_record(base_id, table_name, record_id, api_key):
    endpoint = f'https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}'
    data = {
        "fields": {
            "Name": new_val,
        },
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    response = await pyfetch(
        url=endpoint,
        method='PATCH',
        headers=headers,
        body=json.dumps(data),
    )
    result = await response.json()
    # print(result)


api_key = ''
base_id = 'appiqDH9yo5f9lCwC'
table_name = 'tblzIa6NVYGyQBPdr'
record_id = 'rec4JEibPBPPGQJI6'

# Schedule the coroutine to run
asyncio.ensure_future(patch_record(base_id, table_name, record_id, api_key))
