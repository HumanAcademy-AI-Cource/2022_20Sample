#!/usr/bin/env python3

# 必要なライブラリをインポート
import cv2
import boto3

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
translate_client = boto3.client(service_name="translate")

# 操作案内を表示する
print("[s]キーを押すと認識スタート")

# ループ処理開始
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

            # 一個以上、認識できていたら処理を実行
            if len(face_details) > 0:
                # face_detailsは配列なので、とりあえず一番最初のデータを取り出す
                data = face_details[0]
                # Emotionsの結果だけ取り出す
                emotion_type = data["Emotions"][0]["Type"]

                # ----------------------------
                # Translate
                # ----------------------------
                # 翻訳処理
                translated_text = translate_client.translate_text(
                    Text=emotion_type, SourceLanguageCode="en", TargetLanguageCode="ja"
                )["TranslatedText"]
                # 結果を画面に表示
                print("表情認識の結果: {}({})".format(translated_text, emotion_type))
