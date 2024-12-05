안드로이드개발에 빠질 수없는 MVVM패턴 그에 빠질 수 없는 옵저버 패턴을 구현하기 위해 지금까지 사용했던 LiveData 하지만 안드로이드 디벨로퍼에서는 LiveData를 StateFlow로 교체하여 사용하는 것을 권장한다고 한다.

## Flow가 뭔데 ??

[Android developer](https://developer.android.com/kotlin/flow?hl=ko)
https://stackoverflow.com/questions/58890105/kotlin-flow-vs-livedata

StateFlow전에 Flow에 대해 먼저 알아봐야 할 것 같다. 

> * Flow는 코루틴을 기반으로 빌드되며 비동기식으로 값을 제어할 수 있는 반응형 스트림이다.
* Flow은 **기본 스레드를 차단하지 않는다**

Flow
* CoroutineScrope 내에서 작동한다.
* 생명주기를 감지하지 못한다. `repeatOnLifecycle`과 같은 함수를 사용하여 라이프사이클을 알려줘야함
* Cold Stream이며 상태가 없다. .value의 형태로 값 얻기 불가능

LiveData
* Activity, Fragment 등의 컴포넌트의 생명주기를 인식하며 관찰될 수 있는 데이터들의 집합1
* 메모리 누수가 없음
* 그러나 메인쓰레드에서 라이브데이터는 관찰된다. 

> Repository 래벨에서는 Flow를 사용하고, UI와 레포지토리를 엮는 ViewModel단에서는 Livedata를 사용하기를 추천한다.

Flow의 기본 구조이다.

![](https://velog.velcdn.com/images/cksgodl/post/102f179e-9d99-448d-838e-902ae492e20e/image.png)

**생산자**는 데이터 스트림( 파이프라인 )에 데이터를 생산한다. 이는 코루틴내에서  비동기적으로 데이터가 생산될 수도 있다.

**(선택사항) 중개자**는 스트림에 내보내는 각각의 값이나 스트림 자체를 수정 한다.

**소비자**는 스트림의 값을 사용합니다.

Flow의 구조는 구조자체 [ReactiveX](https://reactivex.io/) 즉 Rx과 동일하다.

![](https://velog.velcdn.com/images/cksgodl/post/f67c004b-7077-4260-b6bf-845cf9c84261/image.png)

#### 생산자는

* emit() 함수를 이용해 새 값을 수동으로 데이터 스트림에 내보낼 수 있다.

또는 [builders](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/)를 이용해 기존 값을 flow로 변환할 수 있다.

* **flowOf(...)** 특정 값으로 Flow을 생성하는 함수

* **asFlow()** 다양한 유형의 값을 Flow로 변환하는 확장 기능

* **flow { ... }** Flow를 빌드하는 빌더 함수

* **channelFlow { ... }** 빌더 함수는 잠재적으로 동시 호출에서 송신 함수로의 임의 흐름을 구성합니다.

* **MutableStateFlow** and **MutableSharedFlow** hot Flow로 변환하여 바로 업데이트될 수 있는 상태로 만든다.

다음과 같은 예는 고정된 간격으로 최신 뉴스를 자동으로 가져오는 예제이다.

```
class NewsRemoteDataSource(
    private val newsApi: NewsApi,
    private val refreshIntervalMs: Long = 5000
) {
    val latestNews: Flow<List<ArticleHeadline>> = flow {
        while(true) {
            val latestNews = newsApi.fetchLatestNews()
            emit(latestNews) // Emit으로 새로운 값을 데이터 스트림에 방출
            delay(refreshIntervalMs)
        }
    }
}

// 비동기로 뉴스 가져오기
interface NewsApi {
    suspend fun fetchLatestNews(): List<ArticleHeadline>
}

```

flow 빌더에서는 생산자가 다른 CoroutineContext의 값을 emit할 수 없다.
그러므로 코드의 withContext 블록을 사용하여 다른 CoroutineContext에서 emit를 호출하지 말기
이땐 새 코루틴을 만들어서 값을 emit하던가 callbackFlow 같은 다른 흐름 빌더를 사용할 수 있다고 한다.


#### 중계자
중간 연사자를 사용하여 값을 소비하지 않고 데이터 스트림을 수정할 수 있다.

```
val favoriteLatestNews: Flow<List<ArticleHeadline>> =
	newsRemoteDataSource.latestNews
    	// Intermediate operation to filter the list of favorite topics
        .map { news -> news.filter { userData.isFavoriteTopic(it) } }
        // Intermediate operation to save the latest news in the cache
        .onEach { news -> saveInCache(news) }
```

#### 소비자

collect 연산자들을 사용하여 데이터 스트림을 가져올 수 있다.
이는 코루틴 내에서 실행되어야 한다
```
viewModelScope.launch {
	newsRepository.favoriteLatestNews.collect { favoriteNews ->
    	// Update View with the latest favorite news
   }
}
```


#### ROOM DB
Room에서는 Flow를 사용하면 데이터 베이스 변경을 알려준다.
```
@Dao
abstract class ExampleDao {
    @Query("SELECT * FROM Example")
    abstract fun getExamples(): Flow<List<Example>>
}
```

---

### StateFlow란?

> StateFlow와 SharedFlow는 흐름에서 최적으로 상태 업데이트를 내보내고 여러 소비자에게 값을 내보낼 수 있는 Flow API이다.

StateFlow란 상태를 가지는 Flow라고 생각하면 될 것 같다.

Android에서 StateFlow는 관찰 가능한 변경 가능 상태를 유지해야 하는 클래스에 아주 적합하다고 하고 이는 즉 LiveData를 대체할 수 있음을 의미한다.

---

**_Flow와의 차이점_** 
Flow는 Cold stream 방식이다.
**Colde Stream**이란 재생버튼을 눌렀을 때 맨 앞에서 재생되는 라디오 같이 Collect를 수행할 때 맨 앞의 값부터 읽어 오게 된다. Flow가 만들어 졌어도 Collect 되기전까지는 이 값이 소비되지 않는다.
 
StateFlow는 **Hot stream** 방식으로 collector가 없어도 생성 시 바로 활성화되며, 값이 업데이트 된 경우에만 반환한다.

Flow는 stateIn 확장함수를 사용하여 StateFlow로 변경 가능하다. 
```
fun <T> Flow<T>.stateIn(
    scope: CoroutineScope, // coroutineScope
    started: SharingStarted,  // 구독을 시작하는 타이밍
    initialValue: T // 초기값
): StateFlow<T>
```

SharingStarted는 다음과 같은 value를 가진다.
* SharingStarted.Eagerly : collector가 존재하지 않더라도 바로 sharing이 시작되며 중간에 중지되지 않음
* SharingStarted.Lazily : 등록된 이후부터 sharing이 시작되며 중간데 중지되지 않음
* SharingStarted.WhileSubscribed : collector가 등록되면 바로 sharing을 시작하며 collector가 전부 없어지면 바로 중지됨

SharingStarted.WhileSubscribed(5000)으로 설정하는것을 권장한다고 한다.
**데이터를 다시 수집하는데 걸리는 시간을 5초로 주는 것
**

---

StateFlow의 경우 초기 상태를 생성자에 전달해야 하지만 LiveData의 경우는 전달하지 않는다.

Flow는 안드로이드의 생명주기를 직접 알 수 없기 떄문에 LifeCycleScope를 확장하여 사용한다.
https://kotlinworld.com/228
포그라운드(onStart, onResume, onPause, onStop 등)에서 안전하게 Coroutine Job을 수행하려면 repeatOnLifecycle을 정의하여 그 안에서만 flow를 collect 해줘야 한다.
```
viewLifecycleOwner.lifecycleScope.launch {
	viewLifecycleOwner.repeatOnLifecycle(State.STARTED) {
		viewModel.data.collectLatest {
	   		  // handle UI
        	}
        }
}
```

이것이 복잡하면 다음과 같이 Extension으로 적용하여 사용할 수 있다.
```
fun <T> Fragment.collectLatestStateFlow(flow: Flow<T>, collect: suspend (T) -> Unit) {
    viewLifecycleOwner.lifecycleScope.launch {
        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            flow.collectLatest(collect)
        }
    }
}

collectLatestStateFlow(viewModel.data) {
	// handle UI            
}

```
기존의 observer를 등록 하듯이 collector를 등록하여 MVVM패턴을 구현할 수 있다.

라이브 데이터를 구현하던 것과 동일한 형식으로 구현하는 방법
```
  private val _lastNameFolderList = MutableStateFlow<ArrayList<GalleryFolder>>(ArrayList())
  val lastNameFolderList: StateFlow<ArrayList<GalleryFolder>> = _lastNameFolderList.asStateFlow()

  fun getImageFolder() {
    viewModelScope.launch {
      _lastNameFolderList.value = galleryPhotoRepository.getLastNameFolderList() // ArrayList를 받아와서 넣기
    }
  }

```

반환값을 Flow로 설정하여 받아오기

```
 val lastNameFolderList: StateFlow<ArrayList<GalleryFolder>> =
    galleryPhotoRepository.getLastNameFolderList() // flow를 반환해야함
      .stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        ArrayList()
      )
      
  override fun getLastNameFolderList(): Flow<ArrayList<GalleryFolder>> = flow {
    val folderList = ArrayList<GalleryFolder>()
	...
    emit(folderList)
  }
     
```

나중에 더추가하기

---

참고자료

https://yjyoon-dev.github.io/android/2022/02/12/android-02/

https://readystory.tistory.com/207

Modern Android Development 입문

https://developer.android.com/kotlin/flow/stateflow-and-sharedflow?hl=ko

https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/state-in.html