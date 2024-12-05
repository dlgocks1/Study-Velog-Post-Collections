## DataBinding이 뭐지??

[Android JetPack ](https://developer.android.com/jetpack?gclid=Cj0KCQjwvLOTBhCJARIsACVldV0idburO_HgY6KWri-1bz9vqkIAN4Cr24pUknT3tshyzhbY1DPy07waAk4JEALw_wcB&gclsrc=aw.ds)라이브러리에서 제공하는 기능 중 하나로써 

(xml파일) 레이아웃을 binding하는데 필요한 코드를 줄이는 방법이다.
보통 MVVM 패턴을 구현 할 때 "LiveData"와 함께 거의 필수적으로 사용한다고 한다.

[developer.android.databinding](https://developer.android.com/jetpack/androidx/releases/databinding)에 의하면
> 레이아웃의 UI 구성요소를 선언적 형식을 사용하여 앱의 데이터 소스에 결합합니다.

### Databinding 사용법

이러한 데이터 바인딩을 사용 설정하려면 아래와 같이 모듈의 build.gradle 파일에서 dataBinding 빌드 옵션을 true로 설정
```
android {
    ...
    buildFeatures {
        dataBinding true
    }
}
```


데이터 바인딩은 레이아웃 바인딩을 xml파일 내에서 직접 수행한다.

 1. 그러기 위해서 xml 최상단 루트를 layout으로 감싸주고,

 2. 사용할 data, vairable 태그를 추가하고 name에는 변수명을, type에는 데이터 바인딩을 통한 이벤트를 세팅할 (내 패키지명 + 액티비티 명 또는 프래그먼트 명 + 모델 명)을 적어주면 됩니다.
 
---
* MainActivity XML
```
<layout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools">

	// XMl 내에서 사용할 변수들을 선언
    // name : 변수 명
    // type : 세팅 할 프래그먼트, 액티비티 or 모델 명
    <data>
        <variable
            name="memoViewModel"
            type="com.jungdarry.bback_coding.viewmodel.MemoViewModel" />

        <variable
            name="mainViewModel"
            type="com.jungdarry.bback_coding.viewmodel.MainViewModel" />
        
    </data>

    <androidx.constraintlayout.widget.ConstraintLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent">
        
        ....
        
    </androidx.constraintlayout.widget.ConstraintLayout>

</layout>

```

---

* MainActivity.kt
```
	private lateinit var memoViewModel: MemoViewModel
    private lateinit var mainViewModel: MainViewModel
    private lateinit var adapter : MemoAdapter

    override fun initView() {
        super.initView()
        
        // Databinding을 수행할 binding을 묶어준다.
        binding = DataBindingUtil.setContentView(this, R.layout.activity_main)
        
        // MainActivity에서 사용할 ViewModel을 정의 
        memoViewModel = ViewModelProvider(this)[MemoViewModel::class.java]
        mainViewModel = ViewModelProvider(this)[MainViewModel::class.java]
        
        //  LifeCycle 및 Xml에 사용할 변수에 모델을 넣어준다.
        binding.lifecycleOwner = this
        binding.memoViewModel = memoViewModel
        binding.mainViewModel = mainViewModel
        }
```

---
* Main ViewModel

```
class MainViewModel : ViewModel() {
	
    // MutableLiveData는 수정이 가능함
    private val _searchText = MutableLiveData<String>()
    private var _ordering = MutableLiveData<Boolean>()

	// LiveData는 외부에서 수정이 불가능하게 설정
    // getter을 사용하여 데이터를 읽는 과정만 수행 가능
    val searchText : LiveData<String>
        get() = _searchText
    val ordering : LiveData<Boolean>
        get() = _ordering

	// LiveData를 수정하는 함수
    fun updateOrdering(ordering:Boolean){
        _ordering.value = ordering
    }

    fun updateSearchText(findstr:String){
        _searchText.value = findstr
    }

    init{
        _searchText.value = ""
        _ordering.value = true
    }

}
```

* Memo ViewModel

### 싱글톤 인스턴스와 ViewModel
Application Context는 기본적으로 Application LifeCycle에 종속되어 있는 싱글턴 인스턴스(인스턴스가 오직 1개만 생성되는 객체)이다.

따라서 현재 액티비티의 LifeCycle이 종료(destroy) 되더라도 GC에 의해 자동 해제되지 않는다.

이러한 특성 때문에 액티비티 수준이 아닌 애플리케이션 수준에서 생성한 싱글턴 오브젝트가 Context를 필요로 하는 경우 Application Context를 사용해야 한다. **싱글턴 인스턴스에서 Activity Context를 사용하면 어떻게 될까?**

싱글턴 인스턴스는 이미 사용되지도 않는, 종료된 액티비티 컨텍스트를 여전히 참조하고 있다. GC는 액티비티 컨텍스트를 Reachable하다고 판단한다.

* GC : 가비지 컬렉터(Garbage Collector, GC)가 주기적으로 검사하여 메모리를 청소해준다

참조를 기준으로 판단하는 GC는 사용되지도 않는 액티비티 컨텍스트의 메모리를 해제하지 않는다.
액티비티 컨텍스트 인스턴스로부터 메모리 누수가 발생한다.
따라서 싱글턴 인스턴스의 경우 애플리케이션 컨텍스트를 전달해주는 것이 바람직하다.
[**싱글톤 인스턴스 출처**](https://velog.io/@dongwan999/10.-%EA%B6%81%EA%B8%88%ED%96%88%EB%8D%98-%EA%B2%83%EB%93%A4-4%ED%8E%B82-Android-Memory-Leak)


**그럼으로 RoomDB의 싱글톤 인스턴스와 ViewModel을 이을 때 Apllication단의 context를 전달해 주는 것이 옳다. **

```
// 만약 ViewModel이 액티비티의 context를 쓰게 되면, 액티비티가 destroy 된 경우에는 메모리 릭이 발생할 수 있다.
// 따라서 Application Context를 사용하기 위해 Applicaion을 인자로 받는다.

class MemoViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = MemoRepository(application)
    private val memos = repository.getAll()

    fun getAll(): LiveData<List<Memo>> {
        return this.memos
    }

    fun getFilterd(findstr : String): LiveData<List<Memo>> {
        val filteredmemos = repository.getFilterMemo(findstr)
        return filteredmemos
    }

    fun insert(memo: Memo) {
        repository.insert(memo)
    }

    fun delete(memo: Memo) {
        repository.delete(memo)
    }
}
```


Memo RoomDB가 싱글톤 패턴으로 정의되어 있다.
[Kotlin에서 싱글톤 패턴간 간단하게 정의하기](https://0391kjy.tistory.com/29)
```
// 싱글톤 패턴으로 정의되어 있는 MemoDatabase Class
@Database(entities = [Memo::class], version = 1)
abstract class MeMoDatabase: RoomDatabase() {

    abstract fun memoDao(): MemoDao

    companion object {
        private var INSTANCE: MeMoDatabase? = null

        fun getInstance(context: Context): MeMoDatabase? {
            if (INSTANCE == null) {
                synchronized(MeMoDatabase::class) {
                    INSTANCE = Room.databaseBuilder(context.applicationContext,
                        MeMoDatabase::class.java, "memo")
                        .fallbackToDestructiveMigration()
                        .build()
                }
            }
            return INSTANCE
        }
    }

}

```

## Observe함수를 통한 LiveData 관측

```
	  	mainViewModel.searchText.observe(this, Observer {
          // it: String!
          // mainViewModel 내에서의 searchText의 값변화를 감지하여 동작을 수행한핟.
          
          // searchText, ordering 을 기반으로 adapter의 filter함수 수행
          adapter.filter(it,mainViewModel.ordering.value.toString().toBoolean())
        })

		// MemoViewModel.getAll()은 ViewModel -> Data Repository -> Data Dao로 이어져 있다.
        // 즉 Data Dao에서 getAll()함수의 변화가 생기면(insert, delete, modeification) observe가 관측한다. 
		memoViewModel.getAll().observe(this, Observer<List<Memo>>{
                memos->//updateUI
            mainViewModel.updateSearchText("")
            adapter.setMemos(memos,mainViewModel.ordering.value.toString().toBoolean())
        })
```

```
//MemoDao의 getAll() 함수
@Query("SELECT * FROM memo ORDER BY date DESC") // ACS DESC
    fun getAll(): LiveData<List<Memo>>
```
Observe 함수를 이용해 View의 값을 바꾸거나,
XMl내에서 text="@{ViewModel.Attribute}" 처럼 직접 값을 넣을 수도 있다.

[예제 Git Hub](https://github.com/dlgocks1/BbackCodingCone)