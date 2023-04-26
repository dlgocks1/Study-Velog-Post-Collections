안드로이드는 `Linux`기반의 오픈소스 소프트웨어 스택들로 구성됩니다.

![](https://velog.velcdn.com/images/cksgodl/post/e3024cb8-7912-4c71-96ec-92f76bc96938/image.png)

# Linux 커널 계층

![](https://velog.velcdn.com/images/cksgodl/post/13207490-7194-4b64-acac-9abbd2dd4261/image.png)

`Android`플랫폼 기반은 `Linux`커널입니다. 안드로이드 계층 최하단에 위치하며, 시스템전체의 중심역할을 합니다.

`Linux`커널 계층에서 담당하는 역할은 다음과 같습니다.

1. 전원관리
2. 보안설정
3. 메모리 관리
4. 하드웨어 관리
5. 네트워크 시스템 관리

# 하드웨어 추상화 계층(HAL)

![](https://velog.velcdn.com/images/cksgodl/post/f6e26623-2dd9-42ec-a217-683ea6a3e96a/image.png)

하드웨어를 다루기 위한 인터페이스를 추상화시켜놓은 곳이 하드웨어 추상화 계층입니다.

Java API 프레임워크에서 카메라, 블루투스 모듈에 엑세스를 호출하면 HAL계층을 통해 하드웨어 모듈을 로드합니다.

# 안드로이드 런타임 계층

![](https://velog.velcdn.com/images/cksgodl/post/13cb8887-9813-4b9d-bf94-d4eef5d58615/image.png)

안드로이드 런타임 계층은 어플리케이션 코드를 운영체제가 실행할 수 있도록 컴파일하는 계층입니다.

API래벨 21버전 이전에는 `Dalvik`이 안드로이드 런타임이였지만, 21이상부터는 앱이 자체 프로세스 내에서 자체 `ART` 인스턴스로 실행됩니다.

두 차이점에 대해서는 [Dalvik과 ART에 대하여]()에서 설명하겠습니다.

# 네이티브 C/C++ 라이브러리 계층

![](https://velog.velcdn.com/images/cksgodl/post/0ccc61fa-a003-4fa0-af0b-e0521fcdb453/image.png)

`ART` 및 `HAL`등의 많은 핵심 `Android`구성 요소와 서비스가 `C`, `C++`로 작성된 네이티브 라이브러리를 필요로 하는 네이티브 코드를 기반으로 빌드됩니다.

네이티브 라이브러리 계층은 `SQLite`, `WebKit`, `OpenGL`안드로이드에 필수적인 라이브러리가 포함되어 있습니다.

- Webkit : 웹 브라우저 엔진
- Libc : 시스템 C 라이브러리
- Media Framework : 오디오 및 비디오 코덱
- SQLite : 모바일을 위한 경량 데이터베이스
- OpenGL : 그래픽 랜더링 담당

# Java API 프레임워크 계층

![](https://velog.velcdn.com/images/cksgodl/post/dd055946-4600-4cc0-a727-ca1d40a7ae0b/image.png)

`Anddroid OS`의 전체 기능은 `Java` 로 작성된 `API`를 활용해 접근이 가능합니다.

이것이 가능한 이유는 기존 네이티브 라이브러리와 안드로이드 런타임 계층이 `Java`로 추상화되어 있기 때문입니다.

- `Content Provider` : 앱끼리의 데이터 공유 지원
- `Activity Manager` : 앱 생명주기 관리 및 백 스택 제공
- `Notification Manager` : 앱이 상태 표시줄에 사용자 지정 알림을 표시할 수 있도록 지원
- `Resource Manager` : 리소스 관리 지원

(4대 컴포넌트)등을 제공하고 있습니다.

# 어플리케이션 계층

![](https://velog.velcdn.com/images/cksgodl/post/c06b076a-8de8-479c-b7f2-e223e6c44320/image.png)

이메일, 캘린더, 주소록 등의 앱을 제공하는 계층입니다. 사용자를 위한 앱으로 작동하며 이 계층을 이용해 개발을 진행하고 있습니다.

# 참고자료

https://developer.android.com/guide/platform?hl=ko

https://sungbin.land/%EC%95%88%EB%93%9C%EB%A1%9C%EC%9D%B4%EB%93%9C%EB%8A%94-%EC%96%B4%EB%96%BB%EA%B2%8C-%EB%8F%8C%EC%95%84%EA%B0%88%EA%B9%8C-2eee02c66d78

https://www.charlezz.com/?p=792
