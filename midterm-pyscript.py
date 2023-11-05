cv2_image = cv2.cvtColor(np.array(cam.raw_image), cv2.COLOR_RGB2HSV)
cv2_image_RGB = cv2.cvtColor(cv2_image, cv2.COLOR_HSV2RGB)

lower = np.array([0, 100, 100])
upper = np.array([70, 255, 255])

mask = cv2.inRange(cv2_image, lower, upper)
display(Image.fromarray(cv2_image_RGB))

kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype=np.uint8)
# display(Image.fromarray(mask))

eroded = cv2.erode(mask, kernel)
# display(Image.fromarray(eroded))
dilated = cv2.dilate(eroded, kernel)
# display(Image.fromarray(dilated))

masked = cv2.bitwise_and(cv2_image_RGB, cv2_image_RGB, mask=dilated)
display(Image.fromarray(masked))
count = np.count_nonzero(dilated)
print(count)
if count > 500:
    print("updating airtable...")

    api_key = 'patHUTHeOmbhBkd56.96a8e2afeea480d41aa27eeb9b01ee74afdd9476994d6219b82dbce8bd67ac73'
    base_id = 'appiqDH9yo5f9lCwC'
    table_name = 'tblzIa6NVYGyQBPdr'
    record_id = 'rec4JEibPBPPGQJI6'

    # Headers to authenticate
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    #################### getting record name
    endpoint = f'https://api.airtable.com/v0/{base_id}/{table_name}'
    response = requests.get(endpoint, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response as JSON
        records = response.json().get('records', [])
        for record in records:
            print(record)
            id = record['id']
            print(id)
            name = record['fields']['Name']
            print(name)
    else:
        print(f'Error: {response.status_code}')

    #################### updating record name
    # endpoint = f'https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}'

    # data = {
    #     "fields": {
    #         "Name": "Ferry lkjnBuilding",
    #     },
    # }
    # response = requests.patch(endpoint, headers=headers, data=json.dumps(data))
    # if response.status_code == 200:
    #     print('Successfully updated the record.')
    #     updated_record = response.json()
    #     print(json.dumps(updated_record, indent=4))
    # else:
    #     print(f'Failed to update the record: {response.status_code}')
    #     print(response.json())

