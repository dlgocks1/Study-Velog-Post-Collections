## 빌드란??

> 안드로이드에서의 빌드는 개발자가 소스 코드를 작성 후 앱 설치 파일 `APK`를 만들기 까지의 실행 과정을 의미합니다.

![](https://velog.velcdn.com/images/cksgodl/post/03d2de11-9154-4ada-91dc-9facf47d7830/image.png)

안드로이드는 기본적으로 리눅스 커널위에 여러 소프트웨어 스택이 쌓인 형태로 리눅스의 빌드와 동일하다고 생각하시면 됩니다.

_리눅스에서의 빌드는 소스 코드를 기계어로 컴파일 한 후 사용되는 라이브러리와의 `Link`를 수행하여 실제 실행 파일로 만드는 과정을 의미합니다._

![](https://velog.velcdn.com/images/cksgodl/post/a7bf4565-4c76-4b06-810f-50be18f1ddb2/image.png)

## 빌드 도구

> 빌드 도구는 외부 라이브러리 추가 및 업데이트 등의 설정 시간을 단축시킵니다. 또한 테스트 실행 및 호환성 체크까지 진행합니다.

안드로이드에서 사용되는 빌드 도구는 `maven`, `gradle`등이 있으며 구글에서는 `gradle`의 사용을 권장하고 있습니다.

`Gradle`내부의 빌드 스크립트를 작성하여

- 앱의 의존성
- 라이브러리
- 리소스 파일
- 빌드 설정

등을 진행합니다.

## 빌드 진행

> 빌드 프로세스는 `Gradle` 빌드 도구가 수행합니다. 빌드 프로세스는 앱의 소스 코드와 빌드 스크립트를 결합하여 `APK` 파일을 생성합니다.

1. 코틀린 컴파일러는 `.kt`파일을 `.class` 바이트코드파일로 변환합니다.

2. `Android SDK`의 `dx` 도구를 사용하여 `.class` 파일들을 `.dex` 파일로 변환합니다.
   ![](https://velog.velcdn.com/images/cksgodl/post/489f63f9-d1e3-4c31-af6f-6a60b3ab3cca/image.png)

3. 안드로이드 리소스 패키징 도구(`aapt`)와 `Gradle` 사용하여 리소스 파일 및 외부 라이브러리 모듈을 `.dex`파일과 함께 APK 파일로 패키징합니다.

4. `APK` 파일은 서명되어야 안드로이드 디바이스에서 실행될 수 있습니다. `APK` 파일에 서명하기 위해서는 디지털 인증서를 사용해야 합니다. `APK` 파일에 서명하는 작업은 빌드 과정에서 `Gradle`에 설정된 값에 따라 자동으로 수행합니다.
   ![](https://velog.velcdn.com/images/cksgodl/post/0f48ca15-e9aa-4c90-9975-a9c876cf6c48/image.png)

이렇게 서명된 `APK`가 만들어 질 수 있습니다.

## APK 설치 및 실행

![](https://velog.velcdn.com/images/cksgodl/post/62309eca-a848-411c-8799-372868d38fb2/image.png)

설치된 `APK`는 [안드로이드 런타임과정](https://velog.io/@cksgodl/Android-Android-Runtime%ED%99%98%EA%B2%BD-ART%EC%99%80-Dalvik%EC%97%90-%EB%8C%80%ED%95%98%EC%97%AC)을 따라 초기 `JIT`방식을 활용하여 앱을 설치한 후, 이후 자주 사용하는 앱을 `AOT`방식을 활용하여 컴파일하는 방식으로 진행됩니다.

각각의 컴파일 방식의 장,단점을 해소하기 위해 이렇게 컴파일을 2번 진행합니다.

## 참고 자료

[이것이 안드로이드다 with kotlin](https://m.hanbit.co.kr/channel/category/category_view.html?cms_code=CMS4183604672)
