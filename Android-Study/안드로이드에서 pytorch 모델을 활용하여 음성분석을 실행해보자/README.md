## Problem

`Pytorch AI`모델을 활용한 `Speech Recognization`을 안드로이드 단에서 구현하고자 한다.

### 인공지능 모델을 만들어야 한다. 어떻게 만들어 할까??

인공지능 모델이 만드는 방법은 크게 두 가지이다.

1. 사전에 학습된 모델을 가져와서 새로운 데이터셋으로 Fine-tuning하여 적절한 모델을 세팅한다.

2. 새로운 모델을 디자인하고 학습시키기 ->
   PyTorch에서 제공하는 nn.Module 클래스를 상속하여 모델 아키텍처를 구성하고 학습을 위한 파라미터를 설정하고 최적화 알고리즘을 활용해 새로운 모델을 생성한다. 이 때 테스트 데이터셋과 검증용 데이터 셋을 분리하여 모델을 학습한 후 검증한다.

---

이러한 과정을 거치면 `****.pt` 또는 `****.ptl(경량화 모델)`의 학습된 모델 파일을 얻을 수 있다.
이제 모델 파일을 가지고 안드로이드 `AI모델`을 통한 `Speech Recognization`을 사용해보자.

[pytorch - android 공식문서](https://pytorch.org/mobile/android/)에서 이미지 `Classification`예제도 제공하고 있다.

## Wav2Vec2 모델을 활용한 Speech-Recognition

예제로 수행할 것은 [Wav2Vec2 모델을 활용한 Speech-Recognition](https://github.com/pytorch/android-demo-app/blob/master/SpeechRecognition/README.md)이다.

1. 예제 앱 클론

```
git clone https://github.com/pytorch/android-demo-app
cd android-demo-app/SpeechRecognition
```

2. 모델 파일 만들기

```
python create_wav2vec2.py
```

![](https://velog.velcdn.com/images/cksgodl/post/6a319672-d20e-4a45-9117-6b7ee0246c6d/image.png)

해당 파일 내부를 확인하면 `nn.module`을 상속받아 새로운 모델을 생성하고

```
optimized_model._save_for_lite_interpreter("wav2vec2.ptl")
```

`wav2vec2.ptl`로 모델파일을 저장해주는 것을 알 수 있다.

3. 모델 파일을 `Assets`폴더에 넣기

```
mkdir -p app/src/main/assets
cp wav2vec2.ptl app/src/main/assets
```

굳이 터미널 안쓰고 넣어도 된다.
![](https://velog.velcdn.com/images/cksgodl/post/555de68e-d5d4-4deb-8ed4-25c836f05b61/image.png)

음성 인식을 위해서는 해당 권한을 허용해 주어야 한다.

```
// Manifest
<uses-permission android:name="android.permission.RECORD_AUDIO" />


// 권한 허용 함수
private fun checkVoiceCommandPermission(context: Context) {
    if (ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.RECORD_AUDIO
        ) != PackageManager.PERMISSION_GRANTED
    ) {
        requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), 100)
    }
}
```

이 후 음성인식을 위한 쓰레드를 생성한 후 레코드를 및 음성 분석을 진행해 보았다.

```
class VoiceVerificationThread(
    private val recognize: (floatInputBuffer: FloatArray) -> String
) : Thread() {
    var isRunning = true

    @SuppressLint("MissingPermission")
    override fun run() {
        while (isRunning) {
            val bufferSize = AudioRecord.getMinBufferSize(
                MainActivity.SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT
            )
            val record = AudioRecord(
                MediaRecorder.AudioSource.DEFAULT,
                MainActivity.SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                bufferSize
            )

            record.startRecording()

            var shortsRead: Long = 0
            var recordingOffset = 0
            val audioBuffer = ShortArray(bufferSize / 2)
            val recordingBuffer = ShortArray(MainActivity.RECORDING_LENGTH)

            while (shortsRead < MainActivity.RECORDING_LENGTH) {
                val numberOfShort = record.read(audioBuffer, 0, audioBuffer.size)
                shortsRead += numberOfShort.toLong()
                System.arraycopy(audioBuffer, 0, recordingBuffer, recordingOffset, numberOfShort)
                recordingOffset += numberOfShort
            }

            record.stop()
            record.release()

            GlobalScope.launch(Dispatchers.Default) {
                val floatInputBuffer = FloatArray(MainActivity.RECORDING_LENGTH)
                // -1.0f and 1.0f 사이로 값 정규화 수행
                for (i in 0 until MainActivity.RECORDING_LENGTH) {
                    floatInputBuffer[i] = recordingBuffer[i] / Short.MAX_VALUE.toFloat()
                }
                val result = recognize(floatInputBuffer)
                Log.i("Result : ", "Result: $result")
            }
        }
    }
}
```

선언된 상수 값들은 다음과 같다.

```
companion object {
    private val REQUEST_RECORD_AUDIO = 13
    private val AUDIO_LEN_IN_SECOND = 5
    val SAMPLE_RATE = 16000
    val RECORDING_LENGTH = SAMPLE_RATE * AUDIO_LEN_IN_SECOND
}
```

위에서 부터 천천히 분석해보자

```
val bufferSize = AudioRecord.getMinBufferSize(
    MainActivity.SAMPLE_RATE,
    AudioFormat.CHANNEL_IN_MONO,
    AudioFormat.ENCODING_PCM_16BIT
)
val record = AudioRecord(
    MediaRecorder.AudioSource.DEFAULT,
    MainActivity.SAMPLE_RATE,
    AudioFormat.CHANNEL_IN_MONO,
    AudioFormat.ENCODING_PCM_16BIT,
    bufferSize
)
```

- `SAMPLE_RATE`
  아날로그 신호를 디지털 신호로 바꿀 때 사용되는 것이 `SAMPLE_RATE`이다.
  ~~_`오인페`를 사용하여 기타나 베이스의 소리를 디지털 신호로 바꿔줄려면 이 `SAMPLE_RATE`를 무조건 맞춰줘야 한다._~~
  오디오 표준은 `44.1khz`인데 이는 즉 1초에 44,100번을 샘플링하여 오디오로 저장한다는 말이다.

- `CHANNEL_IN_MONO`
  오디오 입력 채널을 의미한다. `CHANNEL_IN_MONO`는 1채널 오디오, `CHANNEL_IN_STEREO`는 2채널 오디오를 의미한다.

- `ENCODING_PCM_16BIT`
  오디오 한데이터를 16bit로 표시한다는 의미이다.

이렇게 버퍼사이즈를 정의하고 `AudioRecord`객체를 선언한 뒤, 레코딩을 시작한다.

```
record.startRecording()
```

레코딩이 시작됬으면 레코딩된 값들(`SAPLING_DATA`)를 처리해야 한다.

```
var shortsRead: Long = 0
var recordingOffset = 0
val audioBuffer = ShortArray(bufferSize / 2)
val recordingBuffer = ShortArray(MainActivity.RECORDING_LENGTH)

while (shortsRead < MainActivity.RECORDING_LENGTH) {
    val numberOfShort = record.read(audioBuffer, 0, audioBuffer.size)
    shortsRead += numberOfShort.toLong()
    System.arraycopy(audioBuffer, 0, recordingBuffer, recordingOffset, numberOfShort)
    recordingOffset += numberOfShort
}

record.stop()
record.release()
```

레코딩된 값들을 `recordingBuffer`에 저장한다. 이를 위한 `while`문의 정확한 내용은 다음과 같다.

```
// audioBuffer의 0..audioBuffer.size 크기만큼 레코드를 읽어드린다.
val numberOfShort = record.read(audioBuffer, 0, audioBuffer.size)

shortsRead += numberOfShort.toLong()

// 읽어들인 버퍼크기만큼 계속 recordingBuffer에 추가한다.
System.arraycopy(audioBuffer, 0, recordingBuffer, recordingOffset, numberOfShort)

// 5초까지 계속 녹음을 실시하도록 오프렛 추가
recordingOffset += numberOfShort
```

이후 녹음된 레코드 샘플링 데이터를 `pytorch`모델에게 넘겨 결과를 추론한다.

```
// 코루틴을 활용해 레코딩이 멈추지 않게 함
GlobalScope.launch(Dispatchers.Default) {
    val floatInputBuffer = FloatArray(MainActivity.RECORDING_LENGTH)
    // 인풋데이터 값 정규화 실시 -1~1사이 값으로 변경
    for (i in 0 until MainActivity.RECORDING_LENGTH) {
        floatInputBuffer[i] = recordingBuffer[i] / Short.MAX_VALUE.toFloat()
    }
    val result = recognize(floatInputBuffer)
    Log.i("dlgocks1", "Result: $result")
}
```

지금까지 수행한 것은 쓰레드에서 5초마다 녹음을 한 후 `recognize`함수에 넘기는 것이다.

그리고 음성 분석을 위해 `pytorch`모듈을 불러오자

```
private var mModuleEncoder: Module? = null

// OnCreate
if (mModuleEncoder == null) {
    val moduleFileAbsoluteFilePath: String =
        File(assetFilePath(this, "wav2vec2.pt")).absolutePath
    mModuleEncoder = Module.load(moduleFileAbsoluteFilePath)
}
```

이제 `recognize`함수에서는 어떻게 진행되는지 알아보자.

```
private val recognize: (FloatArray) -> String = { floatInputBuffer ->
    val wav2vecinput = DoubleArray(MainActivity.RECORDING_LENGTH)
    for (n in 0 until MainActivity.RECORDING_LENGTH) {
        wav2vecinput[n] = floatInputBuffer[n].toDouble()
    }
    val inTensorBuffer: FloatBuffer = Tensor.allocateFloatBuffer(MainActivity.RECORDING_LENGTH)
    for (wavInput in wav2vecinput) inTensorBuffer.put(wavInput.toFloat())
    val inTensor: Tensor = Tensor.fromBlob(
        inTensorBuffer, longArrayOf(1, MainActivity.RECORDING_LENGTH.toLong())
    )
    val result = mModuleEncoder?.forward(IValue.from(inTensor))
    result?.toStr() ?: "변환 실패"
}
```

_~~예제 그대로 따라하긴 했지만 이대로 진행될 필요는 없어보임~~_

1. `wav2vecinput`이라는 `Double`형 어레이에 `Float`데이터 값을 변환하여 넣어준다.
2. `inTensorBuffer`를 `SAMPLE_RATE`데이터 수만큼 확보해 준다.
3. `inTensorBuffer`에 `Double`로 변환했던 수를 다시 `Float`으로 변환하여 집어 넣는다
4. `PyTorch` 라이브러리의 `fromBlob()` 함수를 사용하여 `inTensor`라는 새 `Tensor` 객체를 만든다.
   여기서`longArrayOf(1, MainActivity.RECORDING_LENGTH.toLong()`는 해당 텐서객체의 형태를 의미한다. 내부에 이렇게 설계되어 있음
5. `mModuleEncoder.forward()`를 활용하여 결과값을 도출하고 형태에 맞게 `toStr()`, `toDouble()`등의 확장함수를 이용하여 결과를 얻는다.

녹음된 `floatInputBuffer`를 활용하여 5초마다 음성분석이 실행되는 결과를 볼 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/9e8ce218-b298-4b95-b9c2-3164aee7925a/image.png)

---

## 아직 해결하지 못한 문제

`Pytorch` 모델을 활용해 안드로이드에서 모델학습은 권장되지 않으며 관련 소스도 찾을 수 없었다. 기존의 모델을 활용해 결과값을 추론하는 것 까지는 가능해도 모델 학습을 수행하는 것은 불가능한 것 같다.

따라서 대안으로는 클라우드 서비스를 활용하여 모델 학습을 수행하거나, 학습된 모델을 안드로이드 애플리케이션에 넣는 것이라고 한다.
클라우드 서비스로는 `Google Cloud ML Engine`, `Amazon SageMaker` 등의 클라우드 기반 머신 러닝 서비스를 사용할 수 있다고 한다.

## 참고자료

[안드로이드 백그라운드 서비스 ](https://qwerty-ojjj.tistory.com/37)
