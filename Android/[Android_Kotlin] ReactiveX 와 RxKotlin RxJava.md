### 일단 함수형 프로그래밍이 뭔지 알고 가자

어떠한 함수로 들어온 변수들을 짝수만 선택하고, 선택된 값들의 앞의 3번째 값만 선택하여 제곱하여 반환하는 함수가 있다고 생각해보자.

```
fun main() {
    var numbers = arrayOf(1,2,3,4,5,6,7,8)
    println(testFun(numbers))
}

fun testFun(numbers: Array<Int>): MutableList<Int> {
    val result = numbers.filter{ i->i%2 ==0
    }.toMutableList()
    for(i in 0..2){
        result[i] = result[i]*result[i]
    }
    return result
}
```
최적의 소스코드는 아니지만 해당 함수에서 result라는 한번 사용되고 버려지는 변수가 생기게 된다.

이러한 변수들은 소프트웨어 및 함수가 돌아가는 맥락 즉 **상태값**으로 작용하게 된다. 

변수들의 생성은 한두개는 괜찮지만 프로젝트가 커지면 프로그래머에게 고된 노동이 될 수있고, 이러한 값들을 다루는데 있어 변수가 겹치거나, 값을 제대로 변경하는 것을 빼먹을 수도 있다. 

특히 여러 작업이 동시에 돌아가는 멀티스레딩 환경에서는 둘 이상의 스레드가 한 변수에 접근할 때 세마포어, 뮤텍스의 개념과 같이 Critical Section을 제대로 보호해주지 않으면 파악하기도 힘든 오류가 날 수 있다.

그래서 함수형 프로그래밍에서는 변수생성을 최대한 자제하고, 순수함수들을 사용하여 즉 외부의 데이터를 변경하지 않고 받아온 값들을 내부에서 처리해서 밖으로 반환하는 함수들을 사용한다. 물론 이러한 내부함수내에서 변수가 생성되어 사용되긴 하지만, 개발자에게 노출되지 않고 스레드의 교착문제로부터도 안전하다.

```
fun main() {
    var numbers = arrayOf(1,2,3,4,5,6,7,8)
    println(testFun(numbers)) // [4, 16, 36, 64]
    println(testFun2(numbers)) // [4, 16, 36, 64]
}

fun testFun(numbers: Array<Int>): MutableList<Int> {
    val result = numbers.filter{ i->i%2 ==0
    }.toMutableList()
    for(i in 0..3){
        result[i] = result[i]*result[i]
    }
    return result
}

fun testFun2(numbers: Array<Int>): List<Int> {
    return numbers
    .filter{ it%2 == 0 }
    .slice(0..3)
    .map{ it*it }
}
```
testFun2는 확실히 간결하고 보기 깔끔한 것을 확인할 수 있다.
이는 언어의 순수함수들을 가져다 쓰는 방식으로 코딩이 이루어지며 프로그래머는 다양한 함수의 기능과 활용법을 알아두는 것이 중요하다.

#### ReactiveX랑 무슨상관인데??
ReactiveX(이하 rx)는 함수형 프로그래밍과 아주 비슷한 환경을 지니고있다.

rx는 크게 세 요소로 구성되는데
**옵저버블**(Obserable) : 일련의 값들을 발행한다.

이렇게 발행된 데이터들을 흐름 stream이라고 한다.

이 스트림을 흐르는 값들은 배관(pipe)를 거치면서 **연산자**(Operator)들의 손을 거쳐 가공되게 된다.

이는 마지막 **관찰자**(Observer)이자 소비자가 값을 기다리다가 특정 작업을 수행한다.

Observer가 파이프에서 값이 나오는 것을 기다리는 것을 rx에서는 subscribe구독한다고 표현한다.

>구독자가 발행물에 반응 React하는 것이다.

**rx는 시간의 흐름, 사용자의 동작, 네트워크 요청의 결과, 이벤트까지 모두 stream으로 만들어서 파이프라인에 흘려보내 처리한다.**

간단한 얘를 들어보자.
_rxKotlin으로 작성됨_
```
fun main() {
    val observable1 = Observable.create<Array<Int>> {
        it.onNext(arrayOf(1,2,3,4,5,6,7,8,9,10))
        it.onComplete()
    }

    // observer 객체 생성
    val observer = object : Observer<Array<Int>> {
        override fun onSubscribe(d: Disposable?) {
            println("onSubsribe() $d")
        }

        override fun onError(e: Throwable?) {
            println("onError() - $e")
        }

        override fun onComplete() {
            println("onComplete() ")
        }

        override fun onNext(t: Array<Int>) {
        	// 여기서 operator, 연산자들의 역할을 수행
            val result = t.filter{ it%2 == 0 }
             .map{ it*it }
             .take(4)
            println("onNext() - $result")
        }
    }
    // 옵저버블을 subscribe
    observable1.subscribe(observer)
}
```

![](https://velog.velcdn.com/images/cksgodl/post/3d1511bf-99bb-4ef1-9b87-c1e696a9ba64/image.png)

위의 얘제는 파이프라인에 간단한 array를 흘려보냈다.
이는 아주 평면적인 예일 뿐이며 버튼의 터치이벤트, Edittext의 TextChanged이벤트, Retrofit로 받아오는 데이터를 모두 다 스트림으로 흘려보낼 수 있다. 

```
override fun onStart() {
  super.onStart()
  val searchTextObservable = createButtonClickObservable()

  searchTextObservable
      .subscribe { query ->
        showResult(cheeseSearchEngine.search(query))
      }
}
```
위는 같이 버튼을 클릭했을 때 스트림을 파이프라인에 넘겨봤다.

```
myObservable // observable will be subscribed on i/o thread
      .subscribeOn(Schedulers.io())
      .observeOn(AndroidSchedulers.mainThread())
      .map { /* this will be called on main thread... */ }
      .doOnNext{ /* ...and everything below until next observeOn */ }
      .observeOn(Schedulers.io())
      .subscribe { /* this will be called on i/o thread */ }
```
[옵저버블의 사용하는 여러 방법](https://www.raywenderlich.com/2071847-reactive-programming-with-rxandroid-in-kotlin-an-introduction)

Edittext의 TextChanged이벤트를 스트림으로써 파이프라인에 넘겨보자

#### Disposable이란??
Observer가 더이상 필요없거나 Data를 받아오지 않을 때를 위한 객체이다.


```
	// SearchView의 EditText 옵저버블 만들기. rxbinding으로
    // import com.jakewharton.rxbinding4.widget.textChanges 
    val editTextChangeObservable = binding.searchTermEditText.textChanges()
        
	// 구독하는 subcribe 만들기, 옵저버블에 연산자 추가
    val searchEditTextSubScription: Disposable = editTextChangeObservable
        // 글자가 입력되고 0.3초 후에 onNext 이벤트 데이터 흘려보내기
        .debounce(300, TimeUnit.MILLISECONDS)
        //네트워크 요청, 파일 읽기, 쓰기 등 을 IO쓰레드
        .observeOn(Schedulers.io())
		.subscribeOn(Schedulers.single())
        //구독 행위를 통해 이벤트 응답 받기
        .subscribeBy(onNext = {
            Log.d(TAG, "onNext : $it")
            //TODO:: 흘러온 이벤트 데이터로 리사이클러뷰 필터링
                // it.toString()을 이용해 네트워킹 작업...
        }, onComplete = {
            Log.d(TAG, "onComplete")
        }, onError = {
            Log.d(TAG, "onError : $it")
        })
       // 구독을 관리하는 CompositeDisposable을 생성
       myCompositeDisposable.add(searchEditTextSubScription)
```
위에서 예제는 텍스트가 변경될 때 마다,  스트림으로 데이터가 넘어가고 onNext에서 그를 처리한다.
devounce는 0.3초 이내로 아무리 많은 작업이 들어와도 이를 처리하지 않겠다 라는 것이다.

```
// 구독 을 관리하는 변수를 따로 만들어 LifeCycle을 준수한다.
private var myCompositeDisposable = CompositeDisposable()

  override fun onDestroy() {
        //해당 액티비티가 날라갈 때 Observable 다 날리기
        this.myCompositeDisposable.clear()
        super.onDestroy()
    }
    
    override fun initView() {
		.....
	myCompositeDisposable.add(searchEditTextSubScription)
	}
```
이와같이 리소스를 놓아주지 않으면 메모리 릭이 발생 가능하다.

---
추가해야하는 라이브러리

**Rxjava**
메인라이브러리 

**RxKotlin**
코틀린에서 필요한 추가적인 기능 제공

**RxAndroid**
안드로이드에서의 쓰레드를 Rxjava에서 사용하는 스케줄러와 연동하기 위해 사용

**RxBinding**
Edittext 등의 컴포넌트를 옵저버블 형태로 만들어 주는 것 

라고 간단히 정리하면 될 것 같다.
[Retrofit2와 Rxjava연동하기](https://realapril.tistory.com/54)
[ReactiveX 사이트](https://reactivex.io/)
[반응형 프로그래밍이란](https://www.youtube.com/watch?v=KDiE5qQ3bZI)








