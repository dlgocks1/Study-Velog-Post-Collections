# Problem

`Runway`서비스를 만들며 `QA`를 진행하다가 겪은 문제

> 이미지 로딩이 너무 오래 걸려요.


![](https://velog.velcdn.com/images/cksgodl/post/edbc186d-2abb-4bde-8586-4881f98e8155/image.png)

앱 대부분의 서비스가 사진과 관련되어있기에 (쇼룸 추천, 유저 리뷰확인 및 리뷰 추가 등등,,, ) 이미지 로딩이 느리다는 것은 큰 문제점이 될 수 었기에 이를 해결하고자 여러 방안들 찾아봤다.



# Solution

지금 사용하고 있는 이미지 로딩 라이브러리는 `Glide-Compose`
```
implementation "com.github.bumptech.glide:compose:1.0.0-alpha.1"
```
이며 해당 라이브러리는 구글에서 권장하고 메모리 캐싱과 비동기 로딩을 모두 제공하고 있음으로 문제의 여지가 없었다. (없어야 한다 🤔)

`Glide`에서는 `OKHttp`를 활용해 네트워크 요청을 진행한다. 
```
implementation "com.github.bumptech.glide:okhttp3-integration:4.11.0"
```
글라이드 OkHttp 통합 라이브러리에 Gradle 종속성을 추가하면 `Glide`가 자신의 `OkHttp` 커넥션을 사용하여 모든 이미지를 로드한다.

또한 `OKHttp` 클라이언트를 커스텀으로 만들어 다음과 같이 사용할 수 있다.

```
// In Gradle(:app)
kapt "android.arch.lifecycle:compiler:1.1.1"
kapt 'com.github.bumptech.glide:compiler:4.14.2'
    
    
@GlideModule
class RunwayGlideMoudle : AppGlideModule() {

    override fun applyOptions(context: Context, builder: GlideBuilder) {
        // 이미지 불러오는 시간을 보고싶다면 아래 주석을 풀어주세요
        builder.setLogLevel(Log.VERBOSE)
    }

    override fun registerComponents(context: Context, glide: Glide, registry: Registry) {
        val okHttpClient = OkHttpClient.Builder()
            .build()
        registry.replace(
            GlideUrl::class.java,
            InputStream::class.java,
            OkHttpUrlLoader.Factory(okHttpClient)
        )
    }
}
```

해당 `OkHttpClient`에 인터셉터를 달거나, `GlideBuilder`의 `setLogLevel`함수를 활용하여 네트워크 요청 상태를 파악할 수 있다.

그래서 일단 _"얼마나 느린가?"_를 파악해 보았다.

![](https://velog.velcdn.com/images/cksgodl/post/f2f3026e-9c48-4a9f-9e1a-42fe114bdf55/image.png)



```
with size [363x550] in 33263.690974 ms
with size [363×550] in 33265.068181999995 ms
with size [363×550] in 33464.353682 ms
with size [363y5501 in 33464.935974 ms
```

_와우 결과는 상당히 처참했다._

초기 홈화면에서 메인배너 `10개` + 유저 리뷰 사진 최대`20개`를 불러오는데 마지막 리뷰사진을 불러올때까지 `33초`라는 시간이 걸렸다. 

---

이를 해결하기 위해 고분분투 한 결과를 정리해보고자 한다. 


수많은 이미지 로딩 라이브러리 `Glide`, `Coil`, `Picasso`등을 활용해 이미지를 뷰에 넣기위한 과정은 다음과 같다.

1. 서버 `ImgUrl`을 통해 서버 이미지를 읽는다.
2. 프론트단에서 인코드 퀄리티, 리사이즈 등을 통해 비트맵을 뷰에 맞게 조절(축소)한다.
3. 조절(축소)된 이미지를 뷰에 그린다.

이미지 로딩 라이브러리에서 편의성으로 제공해주는 것은 `2번`단계이다.

`Glide`의 예시로는 다음과 같다.

```
RequestOptions()
    .placeholder(R.drawable.img_dummy) // 이미지 로드 전 더미 이미지를 보여줌
    .override(viewSize) // 이미지 사이즈를 뷰사이즈로 설정
    .encodeQuality(80) // 이미지 품질을 80%로 설정
    .format(DecodeFormat.PREFER_RGB_565) // 이미지 포맷을 RGB565로 설정
    .diskCacheStrategy(DiskCacheStrategy.ALL) // 디스크 캐시 전략 설정
    .error(R.drawable.img_error)    // 이미지 로드 실패시 에러 이미지를 보여줌
```

다음과 같은 설정을 사용하면 뷰사이즈에 맞게 이미지 크기를 줄이면서 이미지 품질을 80%로 설정하기에 정말 빠르게 이미지를 뷰에 그릴 수 있다.

또는 `Glide`에서 제공하는 `preaload()`메서드를 활용해 이미지를 불러오기 전에 미리 로딩하여 캐쉬에 저장할 수 있을 것이다.

```
reviews.forEach { item ->
	Glide.with(context)
	.load(item?.imgUrl)
	.signature(ObjectKey(item.imgUrl))
	.preload() // 사전 로드를 사용하여 이미지를 미리 캐시
}
```

`메모리`측면에서는 이만큼 최적화가 될 수는 없을 것이다.

하지만 위의 설정대로 이미지를 불러와도 별다른 효과는 없었다.

> 문제는 `1번`과정에서 이루어졌기 때문이다.

서버로부터 이미지를 불러오는 과정 자체가 너무 오래 걸렸기 때문이다.
![](https://velog.velcdn.com/images/cksgodl/post/ddae6960-8ad5-45cd-ba3a-ff7386001b5e/image.png)

이유는 최소 `2Mb`부터 `15Mb`까지 나가는 이미지 크기에 문제가 있었다.

![](https://velog.velcdn.com/images/cksgodl/post/1212c325-adb0-4b6e-88a2-61e734b0400a/image.png)

`2Mb`의 이미지가 `0.6초`가 걸리는데 이를 `10Mb`가 넘는 이미지를 20개씩 불러오고 있으니 앞의 문제가 일어난 것이다.

이를 해결하기 위해 또 시도해본 것이 몇가지 있다.

### 1. [Glide - how to load multiple images in parallel?](https://stackoverflow.com/questions/45012504/glide-how-to-load-multiple-images-in-parallel)

이미지를 병렬로 불러온다면 로딩속도가 그나마 개선되지 않을까? 라는 생각이 들었다.

그러기위해서

#### 이미지 로드에 사용되는 쓰레드를 따로 생성(20개)하고
```
override fun applyOptions(context: Context, builder: GlideBuilder) {
	builder.setSourceExecutor(GlideExecutor.newSourceBuilder().setThreadCount(20).build())
    builder.setDiskCacheExecutor(GlideExecutor.newSourceBuilder().setThreadCount(20).build())
}
```

* `setSourceExecutor()` : Glide에서 이미지 로드에 사용되는 스레드를 설정

* `GlideExecutor.newSourceBuilder().setThreadCount(20).build()` 메서드는 실행 스레드를 생성


#### OKHttp의 ConnectionPool 늘리기

위에 설명했던것과 같이 `Glide`는 커스텀 `OkHttpClient`를 등록할 수 있다.

한번에 여러 이미지를 불러오니까 여러번 `HttpConnection`이 생성될 것이고 그에 따른 `ConnectionFool`을 증가시키자는 생각이였다.

* `ConnectionFool`이란??
> ConnectionPool은 OkHttp 라이브러리에서 제공하는 커넥션 관리 기능 중 하나로, 동일한 서버에 대한 여러 개의 HTTP 요청을 처리할 때, 커넥션 재사용을 통해 성능을 최적화하는 기능
```
ConnectionPool은 OkHttp 클라이언트 내부에서 유지되는 커넥션 객체를 관리한다.
커넥션 객체는 HTTP 요청을 처리하기 위해 TCP 소켓 연결을 생성하는데, 
매번 새로운 연결을 생성하면 비용이 많이 들어 성능에 악영향을 끼치게 됨.
이를 방지하기 위해 ConnectionPool은 커넥션 객체를 재사용하여 
동일한 서버에 대한 여러 개의 요청에 대해 동일한 커넥션을 사용할 수 있도록 합니다.

ConnectionPool은 기본적으로 5개의 커넥션을 유지하며, 
커넥션을 사용하고 반환함으로써 커넥션 개수를 유지하고 커넥션 객체의 재사용을 가능하게 한다.
또한, ConnectionPool은 일정 시간 동안 사용되지 않은 커넥션을 제거하여 불필요한 자원 사용을 방지함

ConnectionPool은 OkHttp의 OkHttpClient 객체 내부에서 사용되며, 
기본적으로 자동으로 활성화되어 있습니다. 
따라서 일반적인 사용자는 별도의 설정이나 변경 없이도 ConnectionPool을 사용할 수 있다.
```

다음과 같이 60개의 커넥션을 10초동안 유지하도록 변경해 보았다.

```
val okHttpClient = OkHttpClient.Builder()
    .retryOnConnectionFailure(true)
    .connectionPool(ConnectionPool(60, 10, TimeUnit.SECONDS))
    .build()
```

![](https://velog.velcdn.com/images/cksgodl/post/6c8d600d-8f02-4190-8af3-361026ca6546/image.png)

이미지를 모두다 로딩하는데 `5초` ~ `15초`가 걸렸고 이 역시 만족할만한 결과는 아니였다.

---

# 결론

> 결론은 서버개발자에게 이미지 크기를 줄여달라고 요청하였다. 

![](https://velog.velcdn.com/images/cksgodl/post/903426d4-13ae-4537-81ce-f13f28d7bfe3/image.png)

서버에서 던지는 이미지가 `2000px` ~ `4000px`이고 이거 한 장만 불러오는데도 수 초가 걸림으로 어떻게 할 수가 없었다.

가벼운 이미지로 썸네일 이미지를 따로 받는다던가 하면은 어떻게 자연스럽게 구현이 될 수는 있어도 해당 이미지의 크기로는 방도가 없었다.

[테코블 - `이미지 스토리지`의 구축 및 최적화](https://tecoble.techcourse.co.kr/post/2022-09-13-image-storage-server/)에서 한것과 같이 이미지 서버의 최적화도 필요할 듯 하다. (_10Mb짜리 사진을 주는 서버가 나빠_)  


---


* 13Mb : 12초

![](https://velog.velcdn.com/images/cksgodl/post/417727f6-87a2-40dd-a4a2-e7fd6aae36d3/image.png)







