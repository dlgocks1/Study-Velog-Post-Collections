Dalvik과 ART는 안드로이드에서 실행되는 애플리케이션의 런타임 환경(Runtime Environment)을 의미합니다.

안드로이드 계층 중 런타임 계층
![](https://velog.velcdn.com/images/cksgodl/post/53eaf555-85fb-4824-8619-85d8bcde39af/image.png)

에서도 `ART`를 확인할 수 있습니다

과거 구글은 많은 유저층이 사용하는`Java`를 활용해 앱 개발을 지원하였고, 라이센스 문제와 메모리 효율성 문제로 `JVM`환경을 활용하는 것이 아니라 `Dalvik VM`을 활용하였습니다.

## `Dalbik`이란?

> `Dalbik`은 `Api`버전 2.1부터 5.1까지 사용되었던 런타임 환경입니다.

`JIT(Just In Time)`컴파일러를 사용합니다. 이는 실행되는 시점에 필요한 코드만 컴파일하여 실행하는 방식입니다. 따라서 런타임 중에 컴파일을 진행하여 런타임이 느리게 동작할 수 있습니다. (화면 전환, 앱 실행될 떄 마다 코드를 컴파일합니다.)

### 특징

- 앱이 실행되는 순간 자주 사용되는 바이트 코드를 컴파일하여 Machine Code로 변환 후 캐싱하여 RAM에 올립니다.
- 앱 실행 중 latency가 발생합니다.
- ART에 기반에 설치속도가 아주 빠릅니다.
- 컴파일이 빈번하게 일어나기에 배터리소모 및 RAM사용량이 높습니다.

## `ART`이란?

> `ART`는 `Android 4.4`부터 현재까지 적용되는 런타임 환경입니다.

`AOT(Ahead Of Time)` 컴파일러를 사용합니다. 이는 어플리케이션이 설치되는 시점에 코드를 컴파일 하고 미리 캐시하여 실행하는 방식입니다. 이러한 방식으로 어플리케이션 실행 속도가 빠릅니다.

### 특징

- 앱 설치 시 모든 코드를 `Machine Code`로 컴파일하여 앱 패키지 안에 저장합니다.(`AOT파일`)
- 따라서 설치속도가 느립니다.
- 앱 실행시 컴파일을 하지 않아도 되기에 `JIT`의 지연시간이 없습니다.
- 미리 컴파일 후 `odex`, `elf`파일등을 모두 모은 `aot`파일을 저장하기 때문에 용량이 큽니다.

---

![](https://velog.velcdn.com/images/cksgodl/post/2b1baee6-92f4-4b6f-a2bd-41b4e02bdf66/image.png)

`Dalbik`과 `ART`둘 다 기본상태는 `Dex`파일이며 이를 기계어 코드로 변환하는 데에 있어 차이점은 다음과 같습니다.

_DEX파일이 무엇인지는 [`DEX` 파일이란??](https://velog.io/@cksgodl/Android-JAR-AAR-DEX-APK%EC%97%90-%EB%8C%80%ED%95%98%EC%97%AC)을 참고하기_

#### Dalvik 방식에서는

`.dex` 파일을 `dexopt` 툴을 이용해 `.odex` 파일로 변형한 뒤 `DVM`에서 `JIT` 컴파일러로 `.odex` 파일을 기계어로 번역합니다. 변환된 기계어는 RAM에 올려지어 사용됩니다.

#### ART 방식에서는

`.dex` 파일을 `dex2oat` 툴을 이용해 `.dex` -> `.odex` -> `.oat` 파일로 변형한 뒤 `OAT` 컴파일러로 `.oat` 파일을 기계어로 번역합니다.
`.oat` 파일은 `.dex` 파일 + `.odex` 파일 + `elf` 파일(실행 파일) 형식의 기계어를 포함하고 있습니다. (용량이 큽니다.)

> `.odex` 파일은 optimized dex 파일의 약자로 특정 기기에 최적화된 코드로 다른 기기에서 사용할 수 없는 특징을 가집니다.

---

## 현재 - 혼용 사용

Android Nugat(7.0) 버전 이후에는 ART에 AOT와 더불어 JIT 컴파일러까지 탑재하여 혼용으로 사용합니다.

최초 설치시에는 JIT를 사용하여 설치 속도를 높이고 차후 자주 사용되는 앱의 컴파일을 조금씩 하여 AOT 방식으로 전환합니다.

## 참고자료

https://jennysgap.tistory.com/entry/%EC%95%B1%EB%B6%84%EC%84%9D-02-Dalvik-VM-vs-ART-VM

https://softwaree.tistory.com/52

https://s2choco.tistory.com/16
