`6/29 (Sa) pm 1:00 - 6/29 (Sa) pm 6:00` 건국대학교에서 `KotlinConf2024`가 열렸다. 

코틀린 스프링 개발자가 기억할만한 내용들만 간략하게 정리해보았다.


# KotlinConf 2024 Review

![](https://velog.velcdn.com/images/cksgodl/post/9ee8d10d-534d-4b0f-9e73-4ccdcee7957f/image.png)

# 1. What's new in Koltlin? (2.0)

코틀린개발 생태계가 증가하고 있다. 올해 5월에 코틀린 2.0 출시될 예정 (future-ready, fast)

> 주요한 변경점으로써는 **k2컴파일러 활용을 통한 성능개선(최대 2배의 성능 개선 가능)**이 있다.

이외로는

### _Android 및 KMP 관련 포괄된 기능 제공_

+) Kotlin 2.0이후로는 `Jetbrain`의 `Compose Compiler`로 코틀린 버전 호환 가능 (Android)

- `Google`에서 Andorid Lint, Parcelize, KSP, Compose Compiler Plugin 등을 디벨롭 중이며
- KMP 적극 지원
- Compose MultiPlatform Alpha -> Beta
- Compose Web

등 다양한 기능을 출시 준비 중이다.

또한 아래의 Android Lib또한 KMP에서 지원 대기 중이며

- Lifecycle
- ViewModels
- Room

KMP전용 IDE개발 중이다. -> `Fleet`

등등 KMP 및 Compose MultiPlatform 광고에 대한 내용이 주를 이루었다.

# 2. Gradle Version Catalog with KTS

Gradle이란 빌드 자동화 도구를 의미한다.

- 증분 빌드
  - 빌드 과정 상세 제어
- 빌드 캐싱
- 다양한 기능 제공
  - 컴파일러 옵션
  - JVM 옵션

Gradle도 코틀린으로 사용이 가능하다 -> `build.kts`를 의미

이런 코틀린 + 버전 카탈로그를 활용하여 Gradle을 좀 더 쉽게 관리할 수 있다.

### KTS In Gradle

#### `gradle.kts`의 장점

![](https://velog.velcdn.com/images/cksgodl/post/cf822675-3395-4aca-9b4c-9a1a7a7e2c5f/image.png)

- null safe
- 러닝커브 낮음
- 컴파일 정적 타입
- 자바와 비슷한 퍼포먼스

![](https://velog.velcdn.com/images/cksgodl/post/bd8ff791-0ba2-40d2-8759-13da2fe53401/image.png)

퍼포먼스는 비슷하나 아직까진 느리다.
(인터프리터가 라이브러리를 불러오는데 있어 시간이 오래 걸림)

- 빠른 배포가 필요할 때는 고려하면 될지도..?

### gradle version catalog

> Gradle 의존성을 목록으로 관리한다.

- TOML 언어사용
- `Gradle 7.0`이후 사용

설정 과정이 복잡하다.

![](https://velog.velcdn.com/images/cksgodl/post/4847cfc6-65e7-4418-b030-690ddfaf77a8/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/f514f082-c6dc-48e8-bdba-4761e689f8f4/image.png)

`versions`, `liberaies`, `plugins`, `bundles` 등에 관한 정보를 모두 추가한다.

![](https://velog.velcdn.com/images/cksgodl/post/d6313489-0857-40c2-a528-85a45b2f34c2/image.png)

이런 형식으로 gradle의 버전 정보를 입력할 수 있으며, 한 곳에서 모든 모듈의 버전에 대한 정보를 관리할 수 있음 (**의존성 통합 관리**)

> But
>
> 모듈이 많은 프로젝트에서만 효과가 유효
>
> Spring에서는 boot-starter가 적절한 dependency를 들고오고, 이를 통해 관리할 만큼 큰 프로젝트가 없는 것 같음(Android Porject에는 의미 있을 듯 - 특히 `Compose`)
>
> MSA형식으로 모듈이 작게 분리되어 있으면 해당 항목을 적용할만 프로젝트가 존재 X

### buildSRc VS version catalog

- buildSrc : 커스텀 플러그인 관리
- versionCatalog : 오직 의존성 관리

buildSrc가 더 느림 (플러그인도 같이 관리하고, 리컴파일도 해야한다.)

#### [발표자료](https://speakerdeck.com/junjaboy/gradle-version-catalog-with-kts-kotlinconf24-global-v0-dot-1?slide=56)

# 2. Kotlin Language Features 2.0 and Beyond

`Michail Zarecenskij` 발표자료의 번역 본을 리캡

## 새 코틀린 컴파일러 K2

![](https://velog.velcdn.com/images/cksgodl/post/a3e99bb4-6d72-4d43-8feb-85018cb85952/image.png)

### K2 등장 배경

- 몇몇의 언어 기능은 코틀린에서 예상치 못하게 추가됨
  - 컴파일러도 분야가 나뉘어져 있음
    - [코틀린 컴파일러도 백엔드, 프론트엔트가 나뉘어져 있다.](https://munseong.dev/kotlin/k2compiler/#3-kotlin-compiler-frontend)
    - [Road to K2 Compiler](https://velog.io/@cksgodl/Kotlin-The-road-to-K2-compiler-%EB%A6%AC%EC%BA%A1)
   - 컴파일러 유지 보수 및 발전하기 어려움 (초기 개발자 8명이서 백엔드 부분만 특화하여 개발하였기 떄문에 프론트엔드 컴파일러에 대한 발전 부족)
- 컴파일러 플러그인과 IDE의 상호작용
  - 안정된 API의 부재, 엄격하지 않은 계약 관계
- 컴파일러 시간 성능

### 코틀린 2.0의 등장

> 서브 시스템 기능 및 성능 향상 및 컴파일러 도 변화하게 됨

- [What's new in Kotlin 2.0.0](https://kotlinlang.org/docs/whatsnew20.html)
- 프론트엔드 중간 표현 (Frontend Intermediate Representation : FIR)를 활용하여 프론트엔드 컴파일러를 깊이있게 만듦
- 새로운 제어 흐름엔진, 향상된 타입 추론과 레졸루션

#### 유저가 볼 수 있는 변화

- 스마트 캐스트(타입 추론)의 발전

![](https://velog.velcdn.com/images/cksgodl/post/d9a8f159-a807-423e-8326-549926f7d17a/image.png)

- 변수로 부터의 스마트 캐스트

![](https://velog.velcdn.com/images/cksgodl/post/dbf28c45-bbe0-4cdb-af56-10581b4756d3/image.png)

- 인라인 람다 클로져 안에서의 스마트 캐스트

![](https://velog.velcdn.com/images/cksgodl/post/b245b950-5576-454f-9c2c-e83f5cd222b3/image.png)

- 공통 상위 타입으로 타입캐스트

![](https://velog.velcdn.com/images/cksgodl/post/115eab58-37a7-44ad-b23f-71c430d97e32/image.png)
![](https://velog.velcdn.com/images/cksgodl/post/e2d3e12e-0623-485c-bd82-aaa8410ccf1d/image.png)

- GADT(일반화된 ADT) 스타일 스마트 캐스트 지원

![](https://velog.velcdn.com/images/cksgodl/post/f1ae1f39-a300-43dd-8ca8-1ae8fe22a4b9/image.png)

> Sealed Class 활용시 부하 절감

- 널 가능 연산자 호출의 조합 발전

![](https://velog.velcdn.com/images/cksgodl/post/99d6767c-8fb5-4d52-a3b6-6941f3a3a498/image.png)

- 이름 기반 비 구조화 (2.2기반)

![](https://velog.velcdn.com/images/cksgodl/post/e98f4fff-b3af-4bbb-a062-2699906af67c/image.png)

`component`함수가 아닌 JS처럼 구조분해 할당을 제공할 예정(2.2)

- 확장 가능한 데이터 인자(2.2기반)

![](https://velog.velcdn.com/images/cksgodl/post/0c716493-5a04-494d-8dfd-e25b675f3628/image.png)

Default Value가 많은 함수 및 클래스에 대하여 이를 통해 중복된 생성자를 줄일 수 있음

- 에러를 위한 유니온 타입(연구중, 출시예정 X)

![](https://velog.velcdn.com/images/cksgodl/post/a7e5b9d6-6791-470a-be57-1659cb360840/image.png)

T이거나 NotFound이거나 (에러를 다룰 때 유니온 타입 제공)

- 명시적 백킹 필드

![](https://velog.velcdn.com/images/cksgodl/post/59d20cd3-1418-4611-b6d7-d21620e04744/image.png)

#### [발표 자료](https://speakerdeck.com/dalinaum/recap-kotlin-language-features-in-2-dot-0-and-beyond-michail-zarecenskij?slide=3)

# 3. Project Vahalla, Vallue CLass

- Primitive Type
  - 원시 타입
  - 스택 메모리
- Reference Type
  - 참조 타입
  - 힙 메모리

발할라 프로젝트란? -> JVM을 좀 더 효율적으로 써보자.

### Project Valhalla 목표

Flat한 데이터 구조를 가지기.

> `Value Class`의 등장으로 프로젝트 발할라를 구현
>
> 객체(Object)를 생성하지 않고, 원시타입을 포장한 클래스를 만듬(비싸서...) ->` PRIMITIVE CLASS`
>
> 객체지향 구조에서 필요한 `PRIMITIVE CLASS`를 `Value Class`를 통해 구현

---

Value Class는 Kotlin 1.5에서 추가된 내용으로 [해당 내용 참고](https://velog.io/@dhwlddjgmanf/Kotlin-1.5%EC%97%90-%EC%B6%94%EA%B0%80%EB%90%9C-value-class%EC%97%90-%EB%8C%80%ED%95%B4-%EC%95%8C%EC%95%84%EB%B3%B4%EC%9E%90)

- Value Class 굳이? typealise 써도 되지 않을까?

  - [Inline value classes in Kotlin. Comparison with type aliases and data classes.](https://medium.com/@af2905g/inline-value-classes-in-kotlin-comparison-with-type-aliases-and-data-classes-5b225297ffb2)
  - [Value Classes in Kotlin: Good-Bye, Type Aliases!?](https://quickbirdstudios.com/blog/kotlin-value-classes/)

- 성능적 관점에서의 비교
  - Value Class: 객체를 생성하지 않고 인라인으로 처리되므로 메모리 사용량이 적고 성능이 더 좋습니다.
  - Typealias: 단순히 별칭을 부여하는 것이므로 객체 생성에 영향을 미치지 않습니다.
- 타입 안전성
  - Value Class: 새로운 타입을 정의하므로 타입 안전성을 제공합니다.
  - Typealias: 기존 타입에 별칭을 부여하는 것이므로 타입 안전성을 제공하지 않습니다.
- 런타임 성능
  - Value Class: 인라인 처리로 인해 런타임 성능이 향상됩니다.
  - Typealias: 런타임 성능에 직접적인 영향을 미치지 않습니다.

---

### 결론

Value Class는 성능 최적화와 타입 안전성을 모두 제공하므로 성능이 중요한 상황에서 유용하다.

Typealias는 코드의 가독성을 높이는 데 유용하지만 타입 안정성을 제공하지 않는다.

두 기능 모두 성능에 부하가 거의 없다.

#### [발표 자료](https://github.com/esperar/KotlinConf2024)

## Kotlin Script 활용하기

코틀린이란 언어를 활용해 다른 스크립트 언어처럼 빌드 없이 실행 가능 (쉘 스크립트)

- 베타도 아니고, 실험 단계, JVM 환경, 대안이 많다.

그럼에도 쓰는 이유? : 재밌어 보이니까...

+) 설치 방법 및 활용 방법도 복잡하기에 패스

# 4. Refactoring to Expressive Kotlin

**[Refactoring to Expressive Kotlin](https://www.youtube.com/watch?v=UwM3b5D4FjU) 리캡**

### 네이밍

- 서술적인 이름 짓기
- 명확하게
- 기존에 약속된 네이밍 맞추기

### generics

- 다양한 타입의 객체를 다룰 수 있도록 함수를 다양화 가능

- 무곤변성 : 기본 Generic -> 상위 Or 하위 타입 전환이 불가능
- 공변성(out) : 제네릭 타입 매개변수가 반환타입으로 사용될 때 사용하며, 하위 타입으로 반환될 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/e8073932-7de6-4077-9540-849ba5168639/image.png)

- 반공변성(in) : 제네릭 타입 매개 변수가 매개변수로 사용될 때 지정하며, 상위 타입으로 변환될 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/7e4171ba-f9bb-4732-b800-7c7a493cfb54/image.png)

- 상위 타입 제한

![](https://velog.velcdn.com/images/cksgodl/post/47da6229-8a65-418a-a59e-930e7da01251/image.png)

- generic <-> where

https://kotlinlang.org/docs/generics.html

### inline function

바이트 코드 시 함수 call을 방지

- `noinline`을 활용하면 함수 call 진행
- 스코프함수는 모두 `inline`임으로 적절하게 사용

![](https://velog.velcdn.com/images/cksgodl/post/dd1b1059-6d28-4c3c-9157-67ca446aead5/image.png)

### 함수 참조 (Reflection)

함수참조란?

#### [About Kotlin Reflection - Kotlin.lang](https://kotlinlang.org/docs/reflection.html)

![](https://velog.velcdn.com/images/cksgodl/post/fdc54943-ef24-4bec-ad26-9149ca324d16/image.png)


---

이외 Jetpack Animateion, KMP에 대한 세션이 더 있고, 해당 내용은 발표자료를 참고
