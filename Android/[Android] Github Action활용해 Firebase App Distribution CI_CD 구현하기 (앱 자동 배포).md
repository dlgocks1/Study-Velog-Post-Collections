## 배경

기획 및 디자이너가 QA를 하는 과정을 간소화 하기 위해 파이어베이스에서 제공하는 `App Distribution`을 활용할 수 있다.

하지만 `Firebase App Distribution`또한 `APK` or `AAB`를 추출하여 직접 넣어야한다. 이는 꽤나 귀찮다.

_필자의 컴퓨터는 APK 추출만 하면 메모리 사용량이 90%를 찍는다._

![](https://velog.velcdn.com/images/cksgodl/post/79dc3277-3d73-46f7-a9ec-d6c74c93c4cc/image.png)

> 따라서 `Github Action`을 활용해 `develop` 브런치에 커밋이 된다면 `APK`를 자동 추출하여 테스터들에게 이메일로 보내고자 한다.

이후의 설명은 아무것도 모르는 사람도 따라할 수 있도록 간단하게 작성한다.

---

## 앱 자동배포 하기

### Github Action이란?

안드로이드 개발하면서 `Github Action`을 경험하기는 쉽지 않다. 따라서 정말 간단하게 말하면 깃허브에서 제공하는 트리거라고 생각하면 된다.

- 브런치에 커밋됬을 때
- 이슈에 코멘트가 달렸을 때
- 이슈가 달렸을 때
- PR이 달렸을 때 

등 다양한 이벤트 또는 `cronJob`을 트리거하여 깃허브 내에서 특정 작업을 수행할 수 있다. 아래는 실제 사용하고 있는 `Github Actions`예제이다. (`24.01.31` 기준)

_이러한 `Action`는 깃허브 프로젝트의 `/.github/workflows/<액션 이름>.yaml`으로 저장하여 사용한다._

`Github Action`는 실행할 작업을 `job`이라고 하며 이들의 순서를 `step`이라는 단위로 나누어 실행하게 된다. 

깃허브에서는 내부 `runner`를 제공하고 있어 깃허브의 서버 위에서 우리가 지정한 작업이 돌아간다고 생각하면 된다.

```yaml
name: Build & upload to Firebase App Distribution

on:
  push:
    branches: [ dev ] # dev 브런치에 push가 올 때 이벤트 트리거
  workflow_dispatch: # 수동 실행 옵션 (생략가능)

jobs:
  build:
    runs-on: ubuntu-latest # 이후의 jobs들은 ubuntu의 최신버전에서 실행한다.

    env:
      LOCAL_PROPERTIES_CONTENTS: ${{ secrets.LOCAL_PROPERTIES_CONTENTS }} # scerets에서 로컬 프로퍼티 값 변수(LOCAL_PROPERTIES_CONTENTS)로 설정
      GOOGLE_SERVICES_JSON: ${{ secrets.GOOGLE_SERVICES_JSON }} # scerets에서 구글 제이슨 값 변수(GOOGLE_SERVICES_JSON)로 설정

    steps:
      - uses: actions/checkout@v1

      - name: set up JDK 17 # 깃허브 runner에서 돌아가는 환경은 java 17버전으로 설정한다.
        uses: actions/setup-java@v1
        with:
          java-version: 17

      - name: Grant Permission for gradlew # gradlew 에 대한 퍼미션을 허용한다.
        run: chmod +x ./gradlew
        shell: bash

      - name: Decode And Save Keystore Base64 # app.keystoer.jks 키 값을 디코드 해서 app/ksystore.jks로 저장한다. (생략 가능)
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 --decode > app/keystore.jks
          
      - name: Create google-services.json # 환경변수(GOOGLE_SERVICES_JSON) 값의 내용을 기반으로 `app/google-services.json`를 만든다.
        run: echo "$GOOGLE_SERVICES_JSON" > app/google-services.json

      - name: Create local.properties # (LOCAL_PROPERTIES_CONTENTS)를 기반으로 local.properties를 만들고 keystore.jks 위치를 추가해 준다.
        run: |
          echo "$LOCAL_PROPERTIES_CONTENTS" > local.properties
          echo "SIGNED_STORE_FILE=keystore.jks" >> local.properties # 생략가능

      - name: Build debug # APK를 빌드한다. (디버그용)
        run: ./gradlew assembleDebug

      - name: Upload to Firebase App Distribution # 파이어베이스에 앱 디스트리 뷰션에 배포한다.
        uses: wzieba/Firebase-Distribution-Github-Action@v1
        with:
          appId: ${{secrets.FIREBASE_APP_ID}}
          serviceCredentialsFileContent: ${{ secrets.CREDENTIAL_FILE_CONTENT }}
          groups: winey-team
          file: app/build/outputs/apk/debug/app-debug.apk
```

위의 예제를 하나씩 차례차례로 설명하겠다.

---

### local.properties 등록

대부분의 프로젝트에서 외부로 노출되면 안되는 키값, 클라이언트 아이디 값을 `local.properties`에 등록한다.

```
    defaultConfig {
        buildConfigField(
            "String",
            "KAKAO_NATIVE_APP_KEY",
            properties["kakao.native.app.key"] as String
        )
        resValue(
            "string",
            "KAKAO_NATIVE_APP_KEY_FULL",
            properties["kakao.native.app.key.full"] as String
        )
        resValue(
            "string",
            "NAVER_CLIENT_ID",
            properties["naver.client.id"] as String
        )
}
```

당장 사이드프로젝트에 사용하는 키값들만해도 아래와 같이 많다.

```
sdk.dir=
kakao.native.app.key=
kakao.native.app.key.full=
google.oauth.client.id=
base.url=
naver.client.id=
debug.access.token=
debug.refresh.token=
SIGNED_KEY_ALIAS=
SIGNED_KEY_PASSWORD=
SIGNED_STORE_PASSWORD=
SIGNED_STORE_FILE=
```

프로젝트에서는 이 값들을 기반으로 `APK`를 빌드한다. 따라서 이 값들을 `Github.Secrets`에 저장해 두고 `Github Action`에서 꺼내서 써야한다.

_`Github Action` 문법에 따라 `yaml`파일 내부에 `{{ secrets.<시크릿 변수 명> }}`으로 시크릿에 접근할 수 있다._

레포지토리 설정에 들어가서 `Secrets and variables`에 들어가서 레포지토리 시크릿을 등록할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/4b486297-5109-4667-9fc6-042ee4108750/image.png)

`Local Property`값을 복사하여 붙여넣고 사용하자.

![](https://velog.velcdn.com/images/cksgodl/post/014fed2a-bc22-4e8e-85a8-82a086c14fa8/image.png)

`Github Action`에서 다음과 같이 `local.properties`를 깃허브 시크릿에서 들고와서 생성한다. (`local.properteis`를 `gitignore`에 등록하는 건 필수)

```yaml
- name: Create local.properties
	run: |
    	echo "$LOCAL_PROPERTIES_CONTENTS" > local.properties
```

### google-services 등록

파이어베이스를 사용하면 `google-services`를 `app`폴더내에 저장하여 앱을 등록하는 과정을 거쳤을 것이다. 이에 따라 해당 파일도 `CI/CD`단계에서 직접 넣어줘야 한다.

방법은 `local.properties`와 동일하다.

![](https://velog.velcdn.com/images/cksgodl/post/045c9ebf-92ca-4878-94eb-90ec55881fc1/image.png)

`json`내용을 그대로 복붙해서 `secrets`에 등록하면 된다.

`GOOGLE_SERVICES_JSON`이라는 변수명으로 등록하고 위의 소스를 따라하면 `app/google-services.json`파일로 알아서 만들어 줄 것이다.

```yaml
- name: Create google-services.json # 환경변수(GOOGLE_SERVICES_JSON) 값의 내용을 기반으로 `app/google-services.json`를 만든다.
	run: echo "$GOOGLE_SERVICES_JSON" > app/google-services.json
```

### Keystore 등록 (생략 가능)

카카오톡 로그인이나, 구글 로그인을 진행할 때는 해당 디벨로퍼 콘솔내에서 서명된 키를 등록해야 한다. (`SHA키 값`) 따라서 `Keystore`을 등록하지 않고 깃허브에서 `APK`를 뽑아서 배포하게 된다면 구글 로그인이나, 카카오톡 로그인이 디버그용 앱에서 진행되지 않는다.

이를 해결하기 위해 디버그용 `KeyStore`를 만들고 이를 활용해 디버그용 `APK`가 만들어지도록 설정하면 된다.

일단 `debug`일 때 우리가 프로퍼티로 설정한 `keyStore`파일 및 패스워드가 사용되도록 `build.gradle.kts(:app)`을 설정하자.

```
import java.util.Properties

val properties = Properties().apply {
    load(project.rootProject.file("local.properties").inputStream())
}

android {
	
    // ...

	signingConfigs {
        getByName("debug") {
            keyAlias = properties["SIGNED_KEY_ALIAS"] as String?
            keyPassword = properties["SIGNED_KEY_PASSWORD"] as String?
            storeFile = properties["SIGNED_STORE_FILE"]?.let { file(it) }
            storePassword = properties["SIGNED_STORE_PASSWORD"] as String?
        }
    }
```

이는 `local.properties`에서 키값, 키 패스워드, 스토어 키파일 위치, 스토어패스워드 등을 모두 가져와서 디버그 `signingConfig`로 사용하겠다는 의미이다.

`local.properties`에는 대강 다음과 같은 내용이 들어가 있다.

```
SIGNED_KEY_ALIAS=<키 아이디>
SIGNED_KEY_PASSWORD=<키 패스워드>
SIGNED_STORE_PASSWORD=<스토어 패스워드>
SIGNED_STORE_FILE=<스토어 파일 경로>
```

아이디, 패스워드의 경우는 `local.properties`를 시크릿으로 등록할 때 같이 올라가지만, 키스토어 파일의 경우는 파일을 직접 만들어 주어야 한다.

`local.properties`등록 하듯이 복붙하여 넣고 싶지만, 해당 값은 인코딩 문제가 발생하여 그냥 복붙은 안된다.

![](https://velog.velcdn.com/images/cksgodl/post/f2dd7f8b-7304-459c-9f77-94c8767ea3d9/image.png)

따라서 해당 키 값을 `BASE-64`로 인코딩하여 `Github Secrets`에 저장한 후, `Github Action Step`단계에서 이를 디코드하여 파일로 만들어야 한다.

>  `BASE64`로 인코딩을 하게 되면 크기는 커지지만, 안전하게 값을 전송할 수 있다.

[인코딩 사이트](https://www.base64encode.org/)에서 키값은 인코딩하고 그 값을 깃허브 시크릿에 저장한다.

![](https://velog.velcdn.com/images/cksgodl/post/dcc78177-2f04-4936-9feb-1aba7d6b6a9e/image.png)

그리고 해당 값을 활용하여 `app/keystore.jks`파일로 추출하는 `yaml`를 추가한다.

```yaml
	- name: Decode And Save Keystore Base64 # app.keystore.jks 키 값을 디코드 해서 app/ksystore.jks로 저장한다. (생략 가능)
    	run: |
        	echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 --decode > app/keystore.jks
```

`app`폴더 위의 `keystore.jks`로 저장하기에 아래와 같이 `SIGNED_STORE_FILE=keystore.jks`로 키 위치를 지정하면 된다. 

```
   - name: Create local.properties # (LOCAL_PROPERTIES_CONTENTS)를 기반으로 local.properties를 만들고 keystore.jks 위치를 추가해 준다.
        run: |
          echo "$LOCAL_PROPERTIES_CONTENTS" > local.properties
          echo "SIGNED_STORE_FILE=keystore.jks" >> local.properties # 생략가능
```

### APK 빌드

```yaml
      - name: Build debug # APK를 빌드한다. (디버그용)
        run: ./gradlew assembleDebug
```

`gradlew` 명령어를 활용하여 APK를 빌드한다. 빌드한 APK는 `app/build/outputs/apk/debug/app-debug.apk`에 저장되게 된다.

### 파이어베이스 앱 배포

이는 다른사람이 만든 `Firebase-Distribution Action`을 활용한다.

자세한 가이드 는 해당 [깃허브](https://github.com/wzieba/Firebase-Distribution-Github-Action)에서 확인하면 된다.

가이드를 따라가며 파이어 베이스 `appId`와 `serviceCredentialsFileContent`그리고 배포할 그룹과 `file`위치를 해당 플러그인의 사용 예시를 따라서 작성하면 된다.

- [`serviceCredentialsFileContent`만드는 법](https://github.com/wzieba/Firebase-Distribution-Github-Action/wiki/FIREBASE_TOKEN-migration)
- `appId` : 파이어 베이스 앱 아이디 
- `groups` : 파이어베이스 테스트 그룹 아이디

![](https://velog.velcdn.com/images/cksgodl/post/609ebcf8-3ce2-4999-ab45-55f98598ef4d/image.png)

_위의 값들은 모두 `Secret`으로 관리할 것을 권장한다._

- `file` : 위에서 빌드한 `apk` 위치 (프로젝트 설정에 따라 `apk`이름이 다를 수 있음)

```yaml
      - name: Upload to Firebase App Distribution # 파이어베이스에 앱 디스트리 뷰션에 배포한다.
        uses: wzieba/Firebase-Distribution-Github-Action@v1
        with:
          appId: ${{secrets.FIREBASE_APP_ID}}
          serviceCredentialsFileContent: ${{ secrets.CREDENTIAL_FILE_CONTENT }}
          groups: winey-team
          file: app/build/outputs/apk/debug/app-debug.apk
```

이처럼 작성하게 된다면 `dev` 브런치에 커밋됬을 때 자동으로 `APK`를 빌드하여 테스터들에게 배포하게 된다.

![](https://velog.velcdn.com/images/cksgodl/post/ffb43b6d-7009-4936-ba04-655ada99340b/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/200024f8-d659-4966-b0ce-9b9360f2f9d0/image.png)



## 전체 소스

전체 소스 및 설정은 [Winey-Android](https://github.com/AdultOfNineteen/WINEY-Android)에서 볼 수 있다.