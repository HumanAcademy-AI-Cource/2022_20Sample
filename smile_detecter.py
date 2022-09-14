#!/usr/bin/env python3

# 必要なライブラリをインポート
import cv2
import boto3
import subprocess
import wave


def makeAudioFile(path, data):
    # 引数: 音楽ファイルを保存するパス, オーディオデータ
    # オーディオデータから音楽ファイル作成
    wave_data = wave.open(path, "wb")
    wave_data.setnchannels(1)
    wave_data.setsampwidth(2)
    wave_data.setframerate(16000)
    wave_data.writeframes(data)
    wave_data.close()


def speechPolly(speech_text):
    # ----------------------------
    # Polly
    # ----------------------------
    print("発話内容: {}".format(speech_text))
    # 音声合成開始
    speech_data = polly_client.synthesize_speech(
        Text=speech_text, OutputFormat="pcm", VoiceId="Mizuki"
    )["AudioStream"]
    # 音声合成のデータを音楽ファイル化
    makeAudioFile("speech.wav", speech_data.read())
    # 保存したWAVデータを再生
    subprocess.check_call('aplay -D plughw:Headphones {}'.format("speech.wav"), shell=True)


# Webカメラの設定
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
# フレームレート設定
cap.set(cv2.CAP_PROP_FPS, 30)
# 横方向の解像度設定(320px)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
# 縦方向の解像度設定(240px)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Boto3を使ってAWSのサービスを使う準備
# Rekognitionのクライアントを用意
rekognition_client = boto3.client(service_name="rekognition")
# Translateのクライアントを用意
polly_client = boto3.client(service_name="polly")

# 操作案内を表示する
print("[s]キーを押すと認識スタート")
while True:
    # カメラ画像を取得
    success, image = cap.read()
    # 取得したカメラ画像を表示
    cv2.imshow("Camera", image)
    # キー入力を確認
    key = cv2.waitKey(1)
    if key == ord("s"):
        # カメラ画像のファイル名を設定
        image_filename = "camera.png"
        # カメラ画像を保存
        cv2.imwrite(image_filename, image)

        # ----------------------------
        # Rekognition
        # ----------------------------
        with open(image_filename, "rb") as f:
            # 画像を読み込む
            image = f.read()
            # Rekognitionの処理を開始
            response_data = rekognition_client.detect_faces(
                Image={'Bytes': image}, Attributes=["ALL"]
            )

            # レスポンスデータからFaceDetailsを取り出す
            face_details = response_data["FaceDetails"]

            # 一個以上、認識できていたら顔が検出できたことにする
            if len(face_details) > 0:
                # face_detailsは配列なので、とりあえず一番最初のデータを取り出す
                data = face_details[0]
                # Smileの結果だけ取り出す
                smile_value = data["Smile"]["Value"]

                # 笑顔だった場合
                if smile_value == True:
                    speechPolly("笑顔を検出しました。")
                # 笑顔じゃない場合
                else:
                    speechPolly("笑ってください！")
            # 顔が検出できなかった場合
            else:
                speechPolly("顔が検出できませんでした。")
