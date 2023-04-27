## JAR(Java Archive)

Java 언어로 작성된 코드와 관련된 리소스를 포함하는 압축 파일 형식입니다. 안드로이드 앱 개발에서는 주로 안드로이드 라이브러리를 개발할 때 사용됩니다.

```
dependencies {
    // 로컬 .jar 라이브러리 추가
    implementation(fileTree(mapOf("dir" to "libs", "include" to listOf("*.jar"))))

    // 외부 라이브러리 추가 -> 외부 .jar을 다운받아서 추가합니다.
    implementation("com.example.android:app-magic:12.3")
}
```

## AAR(Android Archive)

안드로이드 라이브러리를 더 효과적으로 관리하기 위해 구글이 도입한 새로운 라이브러리 형식입니다. JAR 파일과 유사하지만, 안드로이드 기능(리소스 등)을 지원하는 라이브러리를 더 쉽게 관리할 수 있습니다.

## DEX(Dalvik Excutable)

`APK`파일을 만들 때 개발자가 작성한 코드(`kotlin`이면 코틀린 컴파일러가, `java`이면 자바 컴파일러가 컴파일)가 컴파일하여 `.class`파일로 변환됩니다.
_`.class`파일은 자바 바이트코드라고 생각하시면 됩니다._

그리고 이 `.class`파일들을 하나로 합쳐서 `.dex`파일로 변환됩니다. (이는 안드로이드 SDK에 포함된 툴이 수행합니다.)

변환된 `.dex`파일과 여러 리소스를 합쳐 `APK`파일을 생성합니다.

![](https://velog.velcdn.com/images/cksgodl/post/689c09c0-54be-41aa-917c-819d074204a2/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/c1002829-bb0b-4e3a-b11c-5ba40570c64b/image.png)

## APK(Android Application Package)

`APK`는 안드로이드 플랫폼에 앱을 배포할 수 있는 파일입니다. 컴파일 된 클래스는 `DEX`파일의 형태로 포함시키고 `AndroidManifest.xml`과 리소스등의 파일도 포함됩니다.

설치되는 자세한 과정은 [안드로이드 빌드 과정]()에서 설명하고 있습니다.

## 참고 자료

https://jmoon.co.kr/29
