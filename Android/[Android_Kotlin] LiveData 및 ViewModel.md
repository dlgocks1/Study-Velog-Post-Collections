[Android Developer ViewModel](https://developer.android.com/topic/libraries/architecture/viewmodel)

## ViewModel이란??

> ViewModel 클래스는 수명 주기를 고려하여 UI 관련 데이터를 저장하고 관리하도록 설계됨

ViewModel 클래스를 사용하면 화면 회전과 같이 구성을 변경할 때도 데이터를 유지할 수 있다.

기존에 앱은 화면 회전을 하면 

![](https://velog.velcdn.com/images/cksgodl/post/ce1ce5dd-bf2c-4d28-bedb-65f0f3533217/image.png)

OnPause -> OnStrop ... -> OnCreate -> OnStart
순으로 생명주기가 다시 반복되는 반에 ViewModel Data는 데이터가 유지된다.

### 프래그먼트 간 데이터 공유

 기존에는 Intent, Bundle, SharedPreference등으로 액티비티 또는 프래그먼트 의 정보교환이 이루어 졌다면,

 같은 활동에 포함된 둘 이상의 프래그먼트 또는 액티비티의 커뮤니케이션을 LiveData로 수행한다.

사용자가 목록에서 항목을 선택하는 프래그먼트와 선택된 항목의 콘텐츠를 표시하는 또 다른 프래그먼트가 있는 split-view(list-detail) 프래그먼트의 일반적인 사례를 가정하면?

![](https://velog.velcdn.com/images/cksgodl/post/87769f4d-44b4-461a-91ea-b89ffebc1ccd/image.png)

장바구니라는 View-Model을 하나 만들고 여러 프래그먼트에서 장바구니에 추가하며 정보를 공유할 수 있을 것



## LiveData란?

뷰모델에 들어가는 살아있는 데이터 라이브데이터와 뷰모델은 세트로 들어간다.

LiveData는 관찰 가능한 데이터 홀더 클래스이며

라이브 뷰모델안에 라이브데이터를 넣어놓고 Observe, 관측하면서 정보가 변경되면 뷰모델에서UI Update를 처리합니다.


---

### +) Backing Field와 Backing Properties

[Kotlin Convention](https://kotlinlang.org/docs/coding-conventions.html#names-for-backing-properties)

```
class C {
    private val _elementList = mutableListOf<Element>()

    val elementList: List<Element>
         get() = _elementList
}
```

** get? set? **

getter/setter에 기본적으로 생성되는 속성(property)이다. Kotlin에서는 Class내의 property에 값을 할당할때는 내부적으로 setter가, 값을 불러올때는 getter가 호출된다.

get(),set() 같은 함수가 내부적으로 호출되고, get, set 내에서는 field,를 통해 프로퍼티가 가지고 있는 값에 접근한다 
이렇게 뒤에 숨어잇는 field라는 의미로 Backing Field

```
class User{ 
	var name: String 
    	get() = name set(value) {name = value} }

var count = 0
    set(value) {
        if(value >= 0) field = value
    }

```
** backing property란? **

 backing field 에 맞지 않는 작업을 수행하려면 항상 backing property 를 갖는 코드를 작성
 
```
private var _table: Map<String, Int>? = null
public val table: Map<String, Int>
    get() {
        if (_table == null) {
            _table = HashMap() // Type parameters are inferred
        }
        return _table ?: throw AssertionError("Set to null by another thread")
    }
```

* MutableLiveData는 ViewModel 안에서 해당 데이터가 수정 될 수 있습니다.
* LiveData는 읽을 수 있지만, 변경 되지 않습니다.
* LiveData는 ViewModel 외부에서 데이터를 읽을 수 있으나, 수정되지 않게 하려면 LiveData를 통해 외부에 해당 데이터를 제공 해야 합니다.

외부에서 Livedata를 변경하지 못하게 하고, 내부에서는 변경이 가능하게 하기 위한 구현이 목적입니다. 
-> 클래스의 캡슐화 및 데이터 보호 가능

```
class C {
    private val _elementList = mutableListOf<Element>()

    val elementList: List<Element>
         get() = _elementList
}
```

---



## 뷰모델, 라이브데이터 직접 사용해보기
[dependency 추가](https://developer.android.com/jetpack/androidx/releases/lifecycle#groovy)
```
	def lifecycle_version = "2.5.0-alpha06"

    // 뷰모델 라이브 싸이클 관련
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:$lifecycle_version")
    // ViewModel utilities for Compose
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:$lifecycle_version")
    // 라이브 데이터 - 옵저러 패턴 관련 - 즉 데이터의 변경사항을 알 수 있다.
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:$lifecycle_version")

```

** 뷰 모델 생성 -> 라이브 데이터 관리 **

```

enum class ActionType{
    PLUS, MINUS
}

// 데이터의 변경
// 뷰모델은 데이터의 변경사항을 알려주는 라이브 데이터를 가지고 있다.
class MyNumberViewModel : ViewModel() {

    companion object {
        private const val TAG = "로그"
    }

    // 뮤터블 라이브 데이터 -> 변경 가능
    // 라이브 데이터 - 값 변동 X, Read Only

    //내부에서 설정하는 자료형은 뮤터블로 변경가능하도록 설정
    private val _currentValue = MutableLiveData<Int>()

    // 변경되지 않는 데이터를 가져 올 때 이름을 _ 언더스코어 없이 생성
    // 공개적으로 가져오는 변수는 private이 아닌 public으로 외부 접근 가능하게 설정
    // 하지만 값을 직접 라이브데이터에 접근하지 않고 뷰모델을 통해 가져올 수 있도록 설정
    val currentValue : LiveData<Int>
        get() = _currentValue

    //초기값 설정
    init{
        Log.d(TAG,"MyNumberViewModel - 생성자")
        _currentValue.value = 0
    }

    fun updateValue(actionType: ActionType, input:Int){
        when(actionType){
            ActionType.PLUS ->
                _currentValue.value = _currentValue.value?.plus(input)
            ActionType.MINUS ->
                _currentValue.value = _currentValue.value?.minus(input)
        }
    }

}
```

** 간단한 XML 생성 **

![](https://velog.velcdn.com/images/cksgodl/post/2d01a6e5-045e-47b0-8cfe-c8247f0435b0/image.png)

+, - 버튼을 눌르면 내부 TextView의 값이 EditText 값만큼 변경되도록 하기


```
 	companion object {
        private const val TAG = "로그"
    }
	//사용할 ViewModel 선언
    private lateinit var myNumberViewModel: MyNumberViewModel
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        //뷰모델 프로바이더를 통해 뷰모델 가져오기
        //라이프사이클을 가지고있는 건 자기 자신
        //우리가 가져오고 싶은 뷰모델 클래스 넣어서 뷰모델 불러오기
        myNumberViewModel = ViewModelProvider(this).get(MyNumberViewModel::class.java)

        //뷰모델이 가지고 있는 값의 변경사항을 관찰 할 수 있는 라이브 데이터를 옵저빙
        myNumberViewModel.currentValue.observe(this, Observer {
            Log.d(TAG,"MainActivity - myNumberViewModel - CurrentValue 값 변경 ${it}")
            test_tv.text = it.toString()
        })
        
        //클릭 리스터
        val testClickListener = View.OnClickListener{
            val userinput = test_edittv.text.toString().toInt()
            //뷰모델에서 라이브데이터 값을 변경하는 메소드 실행
            when(it){
                test_pl_bt -> myNumberViewModel.updateValue(ActionType.PLUS,userinput)
                test_mi_bt -> myNumberViewModel.updateValue(ActionType.MINUS,userinput)
            }
        }

        test_mi_bt.setOnClickListener(testClickListener)
        test_pl_bt.setOnClickListener(testClickListener)
   }
```

![](https://velog.velcdn.com/images/cksgodl/post/6a158731-abfe-4fd4-af0c-62ce3bd3d77a/image.png)

OnPause, OnStop 등 실행하거나 화면을 회전해도 값이 유지된다.

![](https://velog.velcdn.com/images/cksgodl/post/78316a79-854a-4539-b0ac-3bcde53f52f9/image.png)


### 요약
1. ViewModel을 생성
2. ViewModel의 데이터를 관찰하는 옵저버 생성
3. ViewModel내에서 함수를 이용하여 라이브데이터를 처리
4. 라이브데이터의 값을 Observe로 관측, 변화가 감지되면 UI 변경 등 처리




---

### backing field 대신에  observe 함수를  ViewModel에 위치시키

```
class MyNumberViewModel : ViewModel() {

    companion object {
        private const val TAG = "로그"
    }

    private val currentValue = MutableLiveData<Int>()
    
	// 반환 값이 필요없을 때, 함수의 반환 타입으로 Unit을 사용한다. 
    // 반환 타입이 Unit이면 함수 끝에 return을 쓰지 않아도 된다.
    fun observe(owner: LifecycleOwner,  onChange: (Int) -> Unit) {
        currentValue.observe(owner, Observer(onChange))
    }
   
    fun updateValue(actionType: ActionType, input:Int){
        when(actionType){
            ActionType.PLUS ->
                currentValue.value = currentValue.value?.plus(input)
            ActionType.MINUS ->
                currentValue.value = currentValue.value?.minus(input)
        }

    }
    
    init{
        Log.d(TAG,"MyNumberViewModel - 생성자")
        currentValue.value = 0
    }
}
```

```
//In MainActivity

myNumberViewModel = ViewModelProvider(this).get(MyNumberViewModel::class.java)

//뷰모델이 가지고 있는 값의 변경사항을 관찰 할 수 있는 라이브 데이터를 옵저빙

myNumberViewModel.observe(this){
	Log.d(TAG,"MainActivity - myNumberViewModel - CurrentValue 값 변경 ${it}")
            test_tv.text = it.toString()
 }
```


[예제 Git Hub](https://github.com/dlgocks1/BbackCodingCone)

