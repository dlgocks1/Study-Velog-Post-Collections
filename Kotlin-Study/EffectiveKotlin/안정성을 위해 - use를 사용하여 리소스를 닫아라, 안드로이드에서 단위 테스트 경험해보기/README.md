## 리소스를 닫아라

더이상 리소스가 필요하지 않을 때, close 메소드를 활용하여 명시적으로 닫아야하는 리소드들이 있다.
코트린/JVM에서 사용하는 이런 리소스가 굉장히 많은데 대표적으론 다음과 같다.

- InputStream과 OutputStream
- java.sql.Connection
- java.io.Reader(FileReader, BufferedReader,CSSParser)
- java.new.Socketrhk 과 java.util.Scanner

이러한 리소스들은 `AutoCloseable`을 상속받는 `Closeable`인터페이스를 구현하고 있다. 이러한 모든 리소스는 최종적으로 리소스에 대한 레퍼런스가 없어질 때 가비지 컬렉터가 처리해주지만, 느리며 그동안 리소스 유지비용이 많이 들어간다. 따라서 더 이상 필요하지 않을 때 `close`메소드를 호출하여 명시적으로 리소스를 반환하는 것이 국룰이다.

코틀린에서는 표준 라이브러리에 use라는 확장함수를 가지고 있는데 이를 사용하여 자동으로 리소스를 반환 할 수 있다.

```
fun countCharactersInFile(path : File) : Int {
	val reader = BufferdReader(FileReader(path))
    readers.use{
    	return reader.lineSequence().sumBy { it.length }
    }
}

context.contentResolver.query.use {
	//...
}

```

파일을 리소스로 사용하는 경우가 많고, 파일을 한 줄씩 읽어 들이는 경우도 많음으로 코틀린에서는 파일을 한 줄씩 처리할 때 활용할 수 있는 useLines함수도 제공한다.

```
fun countCharactersInFile(path : File) : Int {
	File(path).useLines { lines ->
    	return lines.sumBy { it.length }
    }

    or

    File(path).useLines { lines ->
    	lines.sumBy { it.length }
    }
}
```

이렇게 사용하면 메모리에 파일의 내용을 한 줄씩만 유지하므로, 대용량 파일도 적절하게 처리할 수 있다.

> use를 사용하면 Closeable/AutoCloseable을 구현한 객체를 쉽고 안전하게 처리할 수 있다.
> 파일을 처리할 때는 파일을 한 줄씩 읽어 들이는 useLines를 사용하는 것이 좋다.

## 단위테스트란?

코드를 안전하게 만드는 가장 궁극적인 방법은 다양한 종류의 테스트를 하는 것이다.
단위 테스트는 개발자가 작성하며, 개발자에게 유효하다. 어플리케이션 외부적이 아닌 내부적으로 잘 작동하는 확인하는 것이다.

다음과 같은 예를 보자

```
@Test
fun `fib works corretly for ther first 5 positions`(){
	assertEquals(1, fib(0))
    assertEquals(1, fib(1))
	assertEquals(3, fib(2))
	assertEquals(4, fib(3))
	assertEquals(5, fib(4))
}
```

#### 단위테스트에서는 무엇을 확인하는가

- 일반적인 케이스 (usecase, happy path)를 확인한다.
  (간단한 숫자 몇개를 테스트하듯이)
- 일반적인 오류 케이스와 잠재적인 문제를 확인한다.
  예상되는 일반적인 부분, 과거에 문제가 발생했던 부분 등
- 에지 케이스와 잘못된 아규먼트를 테스트한다.
  `Int`형에 `Int.MaX_VALUE`가 들어가는 경우, `nullable`인데 `null`또는 `null값으로 채워진 객체`가 들어가는 경우 등

단위 테스트는 개발자가 만들고 있는 요소가 제대로 동작하는지를 빠르게 피드백해주므로 개발하는 동안 큰 도움이 된다.
테스트는 계속해서 축적되므로, 회귀 테스트도 쉽다.
수동으로 테스트하기 어려운 것들도 확인할 수 있다.

#### 왜 테스트를 작성해야 하는가?

테스트 작성의 **장점**

- 테스트가 잘 된 요소는 신뢰할 수 있다. 요소를 신뢰할 수 있으므로 요소를 활용한 작업에 자신감이 생긴다.
- 테스트가 잘 만들어져 있다면, 리팩토링하는 것이 두렵지 않다. 테스트가 있음으로 리팩터링했을 때 버그가 생기는지 쉽게 확인할 수 있다.
  _레거시 코드를 수정하려고 만지는 것을 두려워하지 않아도 된다._
- 수동으로 테스트하는 것보다 단위 테스트로 확인하는 것이 빠르다. 개발의 전체적인 속도가 빠르고 재밌어진다.

**단점**

- 단위 테스트를 만드는데 시간이 걸린다.
  그러나 장기적으로 좋은 단위 테스트는 `디버깅 시간`과 `버그를 찾는데 소요도는 시간`을 줄여준다. 수동 테스트보다 훨씬빠르고 시간이 절약된다.

- 테스트를 활용할 수 있게 코드를 조정해야 한다. 기존의 소스를 변경하기 어렵긴 하지만 이러한 변경으로 훌륭하고 잘 정립된 아키텍처를 사용하는 것이 강제된다.

- 좋은 단위 테스트를 만드는 것이 어렵다. 남은 개발 과정에 대한 확실한 이해가 필요하다. 잘못 만들어진 단위 테스트는 득보다 실이 크다.

#### 어떤 부분에 테스트를 작성해야 하는가?

- 복잡한 부분
- 계속해서 수정이 일어나고 리팩터링이 일어날 수 있는 부분
- 비즈니스 로직 부분
- 공용 API 부분
- 문제가 자주 발생하는 부분
- 수정해야 하는 프로덕션 버그

---

## Android에서 단위테스트 경험해보기

### 단위테스트에서의 네이밍 컨벤션

[Unit Test Naming Convention](https://medium.com/@stefanovskyi/unit-test-naming-conventions-dd9208eadbea)

- 메소드이름`_`테스트중인상태`_`예상되는결과
  example: isAdult_AgeLessThan18_False

- 메소드이름`_`예상결과`_`테스트중인상태
  example: isAdult_False_AgeLessThan18

- `test`테스트를 수행하는 상태(특징)
  example: testIsNotAnAdultIfAgeLessThan18

- 테스트를 수행하는 상태(특징) = FeatureToBeTested
  example: IsNotAnAdultIfAgeLessThan18

- Should`_`예상 결과값`_`When`_`테스트 중인 상태
  example: Should_ThrowException_When_AgeLessThan18

- When`_`테스트 중인 상태`_`예상 결과
  example: When_AgeLessThan18_Expect_isAdultAsFalse

- Given`_`초기 상태`_`When`_`테스트하는 상황`_`Then`_`예상결과
  example: Given_UserIsAuthenticated_When_InvalidAccountNumberIsUsedToWithdrawMoney_Then_TransactionsWillFail

---

> 메소드이름`_`테스트중인상태`_`예상되는결과
> 를 사용

### ViewModel에서의 UnitTest로 로직 검사하기

컨벤션을 활용하여 테스트를 진행해 보겠다.
테스트를 만들기 위해서는 해당 Class -> Generate -> Test를 활용해 자동으로 테스트클래스를 만들 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/6ea1f52a-f334-498a-ab5d-86202f8ceb92/image.png)

```
class GalleryViewModelTest {
  @Before
  fun setUp() {
  	// 테스트가 실행되기 전에 실행된다.
  	// 초기화 할 변수, 상태 등을 정의한다.
  }

  @After
  fun tearDown() {
  	// 테스트가 끝난 후 실행된다.
  }
}
```

다음은 JUnit4를 사용하여 뷰모델의 로직을 체크하는 단위테스트이다.

```
@RunWith(AndroidJUnit4::class)
class GalleryViewModelTest {

  private val _compositionTags =
    MutableStateFlow<MutableList<Pair<String, String>>>(mutableListOf())
  val compositionTags: StateFlow<MutableList<Pair<String, String>>>
    get() = _compositionTags.asStateFlow()

  @Before
  fun setUp() {
  }

  @After
  fun tearDown() {
  }

  /** 해당함수는 파라미터로 들어온
  *  동일한 Pair객체가 있으면 삭제하고, 없으면 추가하여 _compositinoTags의 값으로 반환한다.  */
  fun handleUpdateCompositionTags(pair: Pair<String, String>) {
    val temp = _compositionTags.value
    if (temp.contains(pair)) {
      temp.remove(pair)
    } else {
      temp.add(pair)
    }
    _compositionTags.value = temp
  }

  @Test
  fun `handleUpdateCompositionTags`_`isDuplicated`_`retrunFalse`() {
    val test1 = Pair("A", "B")
    handleUpdateCompositionTags(test1)
    handleUpdateCompositionTags(test1)
    assertThat(compositionTags.value.contains(test1)).isEqualTo(false)
  }

}
```

`import com.google.common.truth.Truth.assertThat`를 사용하였으며,

Truth 는 Guava 팀에서 개발한 Assertion 테스팅 라이브러리중 하나로, 지금까지 사용했던 Junit4 대신에 사용할 수 있으며 다양한 기능을 제공하여 효율적으로 테스팅 코드를 만들 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/adcfd279-8eb0-4256-a2b9-363c8daa7bf4/image.png)

### Datastore결과 값 체크하는 UnitTest

```
@RunWith(AndroidJUnit4::class)
@Config(sdk = [Q]) // API 29를 타겟으로 테스트
class TokenRepositoryImplTest {

  lateinit var dataStore: DataStore<Preferences>
  private val context: Context = ApplicationProvider.getApplicationContext()

  @get:Rule
  var instantTaskExecutorRule = InstantTaskExecutorRule()

  @Before
  fun setUp() {
    dataStore = PreferenceDataStoreFactory.create(
      produceFile = { context.preferencesDataStoreFile(DATASTORE_NAME) }
    )
  }

  @After
  fun tearDown() {
  }

  suspend fun setData(value: String) {
    dataStore.edit { prefs ->
      prefs[stringPreferencesKey("TOKEN_KEY_TEST")] = value
    }
  }

  suspend fun getData(): Flow<String> =
    dataStore.data.catch { exception ->
      if (exception is IOException) {
        exception.printStackTrace()
        emit(emptyPreferences())
      } else {
        throw exception
      }
    }.map { prefs ->
      prefs[stringPreferencesKey("TOKEN_KEY_TEST")] ?: ""
    }

  @Test
  @ExperimentalCoroutinesApi
  fun `setDataAndGetData_saveAndGetAction_equals`() = runTest {
    setData("TEST_TOKEN")
    var token = getData().first()
    assertEquals(token, "TEST_TOKEN")
  }
}
```

- `private val context: Context = ApplicationProvider.getApplicationContext()`를 활용하여 Application의 Context를 가져올 수 있다.

- JUni4의 Assert를 사용하여 테스트를 진행하였다.

```
  @get:Rule
  var instantTaskExecutorRule = InstantTaskExecutorRule()
```

- 위에 설정한 규칙은 백그라운드 작업과 연관된 모든 아키텍처 컴포넌트들을 같은(한개의) 스레드에서 실행되게 해서 테스트 결과들이 동기적으로 실행되게 하게 해준다.

- `@ExperimentalCoroutinesApi` 및 `runTest`를 이용하여 테스트가 백그라운드의 testscope에서 진행되게 한다.

```
    testImplementation 'org.jetbrains.kotlinx:kotlinx-coroutines-test:1.6.4'
```

### FakeRepository를 만들고 그에 따른 ViewModel 로직 체크하기

![](https://velog.velcdn.com/images/cksgodl/post/2e364f98-5176-4913-b2ae-3bd92edb1070/image.png)

Fake Repository를 이용하여 ViewModel 로직을 실험해보자

```
class FakeCloverRepository {

  fun getClovers() = flow {
    emit(
      GetCloverResponse(
        listOf<CloverCount>(
          CloverCount(1, "Turn"),
          CloverCount(1, "ManyYears")
        ),
        5,
        listOf(
          Ratio("Turn", 50),
          Ratio("ManyYears", 50)
        )
      )
    )
  }
}
```

서버에서오는 `GetCloverResponse`라는 형태의 데이터 구조를 가지고 임의의 값을 넣어서 `flow`로 반환하는 가짜 형태의 서버 데이터를 생성한다.

```
@ExperimentalCoroutinesApi
class CloverViewModelTest {

  private val repository = FakeCloverRepository()

  @Test
  fun `getClovers_onInit_convertToPieChartData`() = runTest {
    repository.getClovers().collectLatest {
      val testData = setpieChartList(it.ratios)
      assertThat(testData.size).isEqualTo(2)
      val testData2 = setRataioList(it.cloverCounts)
      println(testData2.toString())
      // Tests..
    }
  }
}
```

이를 이용하여 실제로 받아온 데이터처럼 이용해 값이 정상적으로 처리되는지 확인한다.
Kotlin에서의 UnitTest에서는 `println()`을 사용하여 값을 중간에 체크할 수 있다.

#### 가짜 레포지토리를 만드는 것보다 쉬운 방법이 있다.

`Turbine`이라는 라이브러리를 사용하는것인데, 이는 kotlinx.coroutines의 Flow 테스팅 라이브러리다.

```
dependencies {
  testImplementation 'app.cash.turbine:turbine:0.9.0'
}
```

`someFlow.test{}`의 형식으로 간단하게 테스트를 진행할 수 있으며 test람다 내의 flow는 차례대로한번씩 소비된다.

```
flowOf("one", "two").test {
	assertThat("one").isEqualTo(awaitItem()) // True
    // Flow 소비 안함 error
}
```

> 테스트 블록 내에서 흐름에서 수신된 모든 Flow를 소비해야하며, 그렇지 않으면 테스트에 실패한다.

```
  @Test
  fun `turbineTest`() = runTest {
    flowOf("one", "two").test {
      assertThat("one").isEqualTo(awaitItem())
      assertThat("two").isEqualTo(awaitItem())
      awaitComplete()
    }
  } // Test Complete!
```

![](https://velog.velcdn.com/images/cksgodl/post/efd4c7a8-af9c-4cc0-89fb-f492b10b0fe1/image.png)
`turbine`내의 test람다 내에서는 수많은 함수를 지원한다.

- `cancelAndIgnoreRemainingEvents` : 캔슬하고 남은 이벤트를 모두 무시한다.
- `cancel` : 현재 Flow 캔슬
- `expectMostRecentItem` : 가장 최근의 Flow를 할당받는다.
  등등...

Flow를 중간에 개발자가 다룰 수 있게 만들어 놨다.

이를 활용해
같은 Scope내에서 Flow들의 처리

```
  @Test
  @ExperimentalCoroutinesApi
  fun turbineTest() = runTest {
    val turbine1 = flowOf(1).testIn(this)
    val turbine2 = flowOf(2).testIn(this)
    assertEquals(1, turbine1.awaitItem())
    assertEquals(2, turbine2.awaitItem())
    turbine1.awaitComplete()
    turbine2.awaitComplete()
  }
```

에러, 실패를 Flow로 처리, Hot Flows 처리, 비동기 Flow처리까지 자세한 건 [turbine-github](https://github.com/cashapp/turbine)를 참고하도록 하자.

참고 자료

https://youngest-programming.tistory.com/m/492

https://developer.android.com/kotlin/flow/test?hl=ko

https://github.com/cashapp/turbine
