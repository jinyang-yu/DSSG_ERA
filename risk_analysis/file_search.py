import time


######### file search
## 1. create a vector store
def create_vector_store(client, name):
    vector_store = client.vector_stores.create(
            name=name
    )
    print(vector_store.id)
    return vector_store.id

## 2. Add the file to the vector store
def add_file_to_vec(client, vec_id, file_id):
    result = client.vector_stores.files.create(
        vector_store_id=vec_id,
        file_id=file_id
    )
    print(result)

## 3. Check status: Wait until the vector store status becomes 'completed'
def wait_for_vector_store(client, vec_id, check_interval=5, timeout=300):
    start_time = time.time()

    while True:
        status = client.vector_stores.retrieve(vector_store_id=vec_id).status
        print(f"Current status: {status}")
        
        if status == "completed":
            print("Vector store is ready.")
            return True
        elif status == "failed":
            raise RuntimeError("Vector store creation failed.")
        
        if time.time() - start_time > timeout:
            raise TimeoutError("Timeout: Vector store did not complete in time.")
        
        time.sleep(check_interval)

def vectorization(client, name, file_id):
    vec_id = create_vector_store(client, name)
    add_file_to_vec(client, vec_id, file_id)
    wait_for_vector_store(client, vec_id)
    return vec_id


### one-time: feed the file to the API once
def extract_risks_pass_once(client, file_id, vec_id, dev_instructions, prompt, model="gpt-4.1-mini-2025-04-14", temperature=0.0):
    response = client.responses.create(
        model=model,
        input=[
            {"role": "developer", 
            "content": dev_instructions},
            {"role": "user", 
            "content": """Based on the contents of the uploaded file, 
            extract all risks mentioned in this file with the following fields **in details:**""" + prompt}
        ],
        text={"format": {"type": "text"}},
        tools=[{"type": "file_search", "vector_store_ids": [vec_id]}],
        temperature=0.0
    )
    return response

### two-pass: feed the file to the API twice

def extract_risks_pass_twice(client, file_id, vec_id, dev_instructions, prompt, model="gpt-4.1-mini-2025-04-14", temperature=0.0):
    ## 1. Count pass
    count_resp = client.responses.create(
        model="gpt-4.1-mini-2025-04-14",
        input=[
            {"role": "developer", "content": "You are a manager in the Enterprise Risk and Assurance Office."},
            {"role": "user", 
            "content": """Based on the contents of the uploaded file, how many distinct risks are described? 
            Respond with only the integer count—no words, no punctuation."""}
        ],
        text={"format": {"type": "text"}},
        tools=[{"type": "file_search", "vector_store_ids": [vec_id]}],
        temperature=0.0,
    )

    raw = count_resp.output_text.strip()
    risk_count = int(raw)  # e.g. 7
    print(f"Found {risk_count} risks.")

    ## 2. Extract pass 
    response = client.responses.create(
        model="gpt-4.1-mini-2025-04-14",
        input=[
            {"role": "developer", 
            "content": dev_instructions},
            {"role": "user", 
            "content": f"""Based on the contents of the uploaded file, 
            extract {risk_count} risks with the following fields **in details** as JSON.""" + prompt}
        ],
        ## JSON schema or not (optional)
        # text={
        #     "format": {
        #         "type":   "json_schema",
        #         "name":   "risk_extraction",
        #         "schema": risk_schema,
        #         "strict": True
        #     }
        # },
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vec_id]
        }],
        ## reasoning model option
        #reasoning={"effort": "high"}
        temperature=0.0
    )
    return response