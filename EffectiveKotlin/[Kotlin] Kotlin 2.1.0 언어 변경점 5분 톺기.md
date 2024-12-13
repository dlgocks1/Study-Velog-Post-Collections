`24.11.27` 코틀린 `2.1.0`버전이 업데이트 되었다. 큰 변화는 없지만 자잘한 내용이 있어 해당 내용 톺아본다.

[What's New in Kotlin 2.1.0](https://kotlinlang.org/docs/whatsnew21.html)


## 목차

- 언어 기능 업데이트 
   - `when` 표현식에서의 가드 조건
   - 비지역 `break` 및 `continue`
   - 다중 달러 문자열 보간 기능

- `K2` 컴파일러 업데이트
   - 컴파일러 검사에 대한 유연성이 향상 
   - `kapt` 구현이 개선 (`Kotlin 1.9`부터 K2컴파일러의 kapt점차 지원 중)

- `Kotlin` 멀티플랫폼
  - `Swift` 내보내기에 대한 기본 지원이 추가되었고, 컴파일러 옵션에 대한 안정적인 `Gradle DSL`이 도입

- `Kotlin/Native`: `iosArm64`에 대한 지원이 개선되

- `Kotlin/Wasm`: 점진적 컴파일 지원 등 여러 업데이트

- `Gradle` 지원: 최신 Gradle 및 Android Gradle 플러그인 버전과의 호환성이 향상, Kotlin Gradle 플러그인 API가 업데이트

- 문서 개선: `Kotlin` 공식 문서에 개선

멀티플랫폼 지원, 백엔드 컴파일러의 변화는 JVM환경에 크게 영향이 없으니 해당  글에선 다루지 않는다.


## 언어 기능 업데이트

#### When 조건문에서 타입 캐스팅이 가능

Guard conditions in when with a subject

```kotlin
sealed interface Animal {
    data class Cat(val mouseHunter: Boolean) : Animal {
        fun feedCat() {}
    }

    data class Dog(val breed: String) : Animal {
        fun feedDog() {}
    }
}

fun feedAnimal(animal: Animal) {
    when (animal) {
        is Animal.Dog -> animal.feedDog()
        // 조건문에서 Animal이 Cat으로 바로 타입캐스팅 가능
        is Animal.Cat if !animal.mouseHunter -> animal.feedCat()
        else -> println("Unknown animal")
    }
}
```

### Non-local break 및 continue

컴파일러의 컴파일 형식 변환으로 인해 `break` 및 `continue`가 람다 내부(`non-local`)에서도 가능해졌다.

```kotlin
fun processList(elements: List<Int>): Boolean {
    for (element in elements) {
        val variable = element.nullableMethod() ?: run {
            log.warning("Element is null or invalid, continuing...")
            continue
        }
        if (variable == 0) return true 
    }
    return false
}
```

### 다중 $$를 활용한 String 추가(interpolation)

```kotlin
val KClass<*>.jsonSchema : String
    get() = $$"""
    {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "$id": "https://example.com/product.schema.json",
      "$dynamicAnchor": "meta"
      "title": "$${simpleName ?: qualifiedName ?: "unknown"}",
      "type": "object"
    }
	"""
```

문자열 앞에 `$$`을 활용하여 `$`가 변수로 치환되는 것을 방지한다. 변수를 치환하고자 한다면 `$${variable}`을 활용하라.

### 하위 API 확장에 `ope-in` 지원

`@SubclassOptInRequired` 선언자를 활용하여 해당 인터페이스를 상속받는 모든 객체는 `OptIn` 인터페이스를 선언하도록 `warning`이 발생한다.

- 단 이너클래스나, 중첩 클래스는 불가능
- `Kotlin 1.8`에 이미 추가되어 있음, 차이점이 무엇인지는 안적혀있음

```kotlin
@RequiresOptIn(
    level = RequiresOptIn.Level.WARNING,
    message = "Interfaces in this library are experimental"
)
annotation class UnstableApi()

@SubclassOptInRequired(UnstableApi::class)
interface CoreLibraryApi

@OptIn(UnstableApi::class)
interface MyImplementation: CoreLibraryApi
```

### 확장 함수 대한 타입해상도 향상

일반 유형 함수 및 확장 함수유형의 제네릭 타입이 일관되게 동작하지 않는 점 수정

```kotlin
class KeyValueStore<K, V> {
    fun store(key: K, value: V) {} // 1
    fun store(key: K, lazyValue: () -> V) {} // 2
}

fun <K, V> KeyValueStore<K, V>.storeExtension(key: K, value: V) {} // 1
fun <K, V> KeyValueStore<K, V>.storeExtension(key: K, lazyValue: () -> V) {} // 2

fun test(kvs: KeyValueStore<String, Int>) {
    // Member functions
    kvs.store("", 1)    // Resolves to 1
    kvs.store("") { 1 } // Resolves to 2

    // Extension functions
    kvs.storeExtension("", 1)    // Resolves to 1
    kvs.storeExtension("") { 1 } // ERROR : Overload resolution ambiguity
    kvs.storeExtension<String, Int>("") { 1 } // Resolves to 2
}
```

### Sealed 클래스를 포함한 when문의 완전성 검사 개선

_왜 이걸 `2.1.0`에 되서야 지원해 주지_

```kotlin
sealed class Result
object Error: Result()
class Success(val value: String): Result()

fun <T : Result> render(result: T) = when (result) {
    Error -> "Error!"
    is Success -> result.value
    // Requires no else branch
}
```

## K2 컴파일러 업데이트

> K2 모드 안정화
>
> `IntelliJ IDEA 2024.3`에서는 `K2` 모드가 안정화되어 일반적으로 사용할 수 있게 되었다. `K2` 모드는 `Kotlin` 코드 분석의 안정성, 메모리 효율성, `IDE`의 전반적인 성능을 크게 향상시키며, `Kotlin 2.1` 언어 기능을 지원한다.


### 추가적인 컴파일러 체크

이중 `nullable` 타입(`Boolean??`)이나 플랫폼 클래스`(java.lang.String)` 대신 `Kotlin` 클래스`(kotlin.String)`를 사용하는지 검사할 수 있다.

### 글로벌 warning suppression

컴파일 옵션을 추가하여 특정 워닝이 나오지 않게 할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/5e01e3dd-3dcc-418e-babf-21552d7f1928/image.png)

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        extraWarnings.set(true)
        freeCompilerArgs.add("-Xsuppress-warning=CAN_BE_VAL")
    }
}
```

### kapt 구현 개선

`Kotlin 1.9.20`부터 `K2` 컴파일러를 위한 `kapt` 플러그인의 실험적 구현이 도입 중이다. 하지만 아직 알파단계이고 피드백좀 부탁한다. -> [YouTrack](https://youtrack.jetbrains.com/issue/KT-71439/K2-kapt-feedback?_gl=1*k3iam2*_gcl_au*NDIxNTMxMjE5LjE3MjgzNTI2NjQ.*_ga*NjM3NjIzMDk5LjE2OTM4MDIzNjY.*_ga_9J976DJZ68*MTczNDA2ODU3Mi42My4xLjE3MzQwNzEyMTguNjAuMC4w)

그래들에 설정 추가하면 된다.

```
kapt.use.k2=true
```


### unsigned 및 non-primitive 타입에 대한 오버로드 충돌 해결

- 확장 함수 충돌 해결

```kotlin
fun Any.doStuff() = "Any"
fun UByte.doStuff() = "UByte"

fun main() {
    val uByte: UByte = UByte.MIN_VALUE
    uByte.doStuff() // Overload resolution ambiguity before Kotlin 2.1.0
}
```

- 최상단 함수 충돌 해결

```kotlin
fun doStuff(value: Any) = "Any"
fun doStuff(value: UByte) = "UByte"

fun main() {
    val uByte: UByte = UByte.MIN_VALUE
    doStuff(uByte) // Overload resolution ambiguity before Kotlin 2.1.0
}
```

이전 `K1` 컴파일러는 확장함수나 최상단 함수일 때 `Any` 버전을 사용할지 `UByte` 버전을 사용할지 결정하지 못했다.

컴파일 방식의 변화로써 `2.1.0`에서는 이제 이러한 경우를 올바르게 처리하여 더 구체적인 유형인 `UByte`에 우선순위를 두어 모호성을 해결한다.


### 이외 업데이트 사항

#### 표준 API변화

- 지역화에 의존적인 대소문자 변환 함수 사용 중단
  - 함수: Char.toLowerCase(), Char.toUpperCase(), String.toUpperCase(), String.toLowerCase()
  - 대체 방법:
지역화 비의존적 변환: String.lowercase() 또는 String.uppercase() 사용.
   - 특정 지역화 유지: String.lowercase(Locale.getDefault())를 명시적으로 호출.
- appendln() 함수 사용 중단
   - 대체 방법: StringBuilder.appendLine() 또는 Appendable.appendLine() 사용.
   - 이유: appendln()은 플랫폼마다 다른 line.separator 값을 사용했으나, appendLine()은 일관되게 \n(LF)을 사용하여 플랫폼 간 일관성을 유지.


#### gradle 지원 버전 변화

- Kotlin 2.1.0과 Gradle 호환성
  - Kotlin 2.1.0은 Gradle 7.6.3 ~ 8.6까지 완벽하게 호환
  
  



