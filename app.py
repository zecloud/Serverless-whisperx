import os
import datetime
import base64
import requests
from dapr.ext.grpc import App, BindingRequest
from io import BytesIO
import whisperx
import json
from dapr.clients import DaprClient
""" from flask import Flask,request
app = Flask(__name__) """

#code
daprPort = os.getenv('DAPR_HTTP_PORT')
daprGRPCPort = os.environ.get('DAPR_GRPC_PORT')
hftoken = os.environ.get('YOUR_HF_TOKEN')
#print('>>>>>>>>DAPR_HTTP_PORT : '+ daprPort )
#print('>>>>>>>>DAPR_GRPC_PORT : '+ daprGRPCPort )
app = App()
#@app.route("/queueinput", methods=['POST'])
@app.binding('queueinput')
def incoming(request: BindingRequest):
    #incomingtext = request.get_data().decode()
    incomingtext = request.text()
    print(">>>>>>>Message Received: "+ incomingtext,flush=True)
    
    outputfile = "/outputs/Msg_"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")+".txt"
    done = process_message(incomingtext,outputfile)
    if done:
        print('>>>>>> Transcribe done.',flush=True)
        with DaprClient() as d:
             
        
        #url = 'http://localhost:'+daprPort+'/v1.0/bindings/bloboutput'
        #contents = '{ "operation": "create", "data": {"message": "'+ outputfile+ '"} }'
        #print(uploadcontents)
        #requests.post(url, data = contents)
            #req_data = {"message": "'+ outputfile+ '"} 
            resp = d.invoke_binding('queueoutput', 'create', json.dumps(outputfile))
            print('>>>>>> Transcribe done.',flush=True)
            d.close()
            app.stop()
            #d.shutdown()

    return "Incoming message successfully processed!"

def process_message(audio_file,text_file):
#import gc 
    device = "cuda" 
    #audio_file = "audio.mp3"
    batch_size = 16 # reduce if low on GPU mem
    compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)

    # 1. Transcribe with original whisper (batched)
    model = whisperx.load_model("large-v2", device, compute_type=compute_type)

    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)
    print(result["segments"]) # before alignment

    # delete model if low on GPU resources
    # import gc; gc.collect(); torch.cuda.empty_cache(); del model

    # 2. Align whisper output
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

    print(result["segments"]) # after alignment

    # delete model if low on GPU resources
    # import gc; gc.collect(); torch.cuda.empty_cache(); del model_a

    # 3. Assign speaker labels
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=hftoken, device=device)

    # add min/max number of speakers if known
    diarize_segments = diarize_model(audio_file)
    # diarize_model(audio_file, min_speakers=min_speakers, max_speakers=max_speakers)

    result = whisperx.assign_word_speakers(diarize_segments, result)
    print(diarize_segments)
    print(result["segments"]) #
    with open(text_file, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
                #f.writelines(segment["text"].strip())
                print(segment["text"].strip(), file=f, flush=True)
    return True

if __name__ == '__main__':
    app.run(50051)
    with DaprClient() as d:
        d.shutdown()
    #app.run(host="localhost", port=6000, debug=False)