# 2장 자동 메모리 관리

## 자바 메모리 영역과 메모리 오버플로우

C, C++개발자는 메모리관리에 대한 전권을 다 가지고 있다. 객체의 일생을 탄생부터, 죽음까지 관리하기 떄문이다. 그러나 자바 개발자는 JVM이 제공하는 자동 메모리 관리 메커니즘 덕에 메모리 할당과 해제를 신경쓰지 않아도, 누수나 오버플로 문제를 거의 겪지 않는다. 이는 편하긴 하지만, JVM의 메모리 관리에 대해 이해하지 못하고 있다면 문제가 일어났을 때 대처하기 힘들 것이다.


### 2.2 런타임 데이터 영역

JVM은 메모리를 몇 개의 데이터 영역으로 나누어 관리한다. 

![](https://velog.velcdn.com/images/cksgodl/post/6f87ef63-539c-434e-ac93-4481ffcedf06/image.png)

대중적으로 알고 있듯이, 쓰레드가 공유하는 데이터 영역 및 쓰레드별 데이터 병역(스레드 프라이빗)영역으로 나뉘게 된다.

#### PC(program counter)

프로그램 카운터 레지스터는 작은 메모리 영역으로, __현재 실행 중인 스레드에 존재하는 다음 실행할 바이트코드 줄 번호 표시기이다.__

JVM에서 멀티스레딩은 CPU 코어를 여러 스레드가 교대로 사용하는 방식으로 구현되기에 쓰레드 컨텍스트 스위칭이 일너가데 된다. 따라서 멈춘 지점을 정확하게 복원하려면 쓰레드 별 각각의 PC가 필요하다.

__이러한 쓰레드카운터는 서로 영향을 주지 않는 독립된 영역에 저장되며 이를 스레드 프라이빗 메모리라고 한다.__


#### 스택(Stack memory)

스택도 스레드 프라이빗하며, 각 메서드가 호출될 때 마다 JVM은 스택 프레임을 만들어 지역 변수 테이블, 피연선자 스택, 동적 링크 등의 정보를 저장한다. 메서드가 실행되거나 종료되면 JVM에 Push하고, Pop하는 일을 반복한다.

> 자바의 메모리를 힙 메모리와 스택메모리로 구분하는 살마이 많다. 이는 반정도는 맞는 소리이나, 자바의 메모리 영역 구분은 훨씬 복잡하다.(이후 설명)

JVM은 스택 깊이가 허용치를 넘으면. `StackOverflow`, 여유 메모리가 충분하지 않으면 `OutOfMemoryError`를 던진다.


#### 네이티브 메서드 스택

네이티브 메서드 스택는 자바 코드가 컴파일되어 생성되는 바이트 코드가 아닌 실제 실행할 수 있는 기계어로 작성된 프로그램을 실행시키는 영역이다.

이도 동일하게 `StackOverFlow`, `OutOfMemoryError`를 유발할 수 있다.

#### 자바 힙(Java heap)

힙은 자바 어플리케이션이 사용할 수 있는 가장 큰 메모리이다. 자바 힙은 모든 스레드가 공유하며 가상 머신이 구동될 때 만들어진다. 힙의 유일한 목적은 객체 인스턴스를 저장하는 것이고, 자바 세계의 거의 모든 객체 인스턴스가 이 영역에 할당된다.

+) 자바 힙은 가비지 컬렉터가 관리하는 메모리 영역이기 때문에 어떤 문헌에서는 GC힙이라고도 한다. GC에 관해서는 [__3장__]()에서 더 설명할 예정이다.

메모리 관점에서 힙은 모든 스레드가 공유한다. 따라서 객체 할당 효율을 높이고자 쓰레드 로컬 할당 버퍼 여러개로 나뉜다. (어떻게 나뉘든 상관없이 자바힙에 저장되기는 한다.) 이렇게 여러 버퍼로 나누는 이유는 메모리 회수와 할당을 더 빠르게 하기 위함이다. 

힙 메모리는 물리적으로 떨어진 메모리에 위치해도 상관없으나 논리적으로는 연속이여야 한다. 자바 힙은 크기를 고정할 수도, 확장할 수도 있게 구현되어 있다. 요즘 주류 가상 머신들은 모두 확장 가능한 형태로 구현되어 있다.(`Xmx, Xms`활용) 새로운 인스턴스에 할당해 줄 힙 공간이 부족하면 GC가 일어나고, 이를 통해서도 더 확장할 수 없으면 `OOM`를 던진다.

#### 메서드 영역(Method Area)

메서드 영역도 힙 처럼 모든 스레드가 공유한다. 메서드 영역은 가상 머신이 읽어 들인 타입 정보, 상수, 정적 변수 그리고 JIT컴파일러가 컴파일한 코드 캐시를 저장하는데 사용된다.

> JIT (Just-In-Time) 컴파일러는 런타임 시 바이트 코드를 원시 시스템 코드로 컴파일하여 Java 애플리케이션의 성능을 향상시키는 컴파일러다. 

메서드 영역의 메모리는 거의 회수될 일이 없다. (그렇다고 데이터가 영구적이라는 뜻은 아니다.) 메서드 영역에서 회수할 대상은 거의 대부분 상수 풀과 타입이라서 회수 효과가 매우 작으며, 회수 조건이 상당히 까다롭기도 하다.


#### 런타임 상수 풀

이는 메서드 영역의 일부이며, 클래스 버전 및 필드, 메서드, 인터페이스 등 클래스 파일에 포함된 설명 정보에 더해 컴파일타임에 생성되는 리터럴과 심벌 참조가 저장된다. 이러한 정보를 메서드 영역의 런타임 상수 풀에 저장한다.

상수 풀은 컴파일에 미리 생성되지 않아도 되며, 런탕미에도 새로운 상수가 추가될 수 있다.(String클래스의 intern()메서드 참고)

#### 다이렉트 메모리

이는 JVM에 포함되지 않는다. 이는 네이티브 메서드를 통해 메모리에 저장되어 있는 DirectByteBuffer 객체를 통해 작업을 수행할 수 있다. (힙과 네이티브 힙 사이에서 데이터를 주고받지 않아도 돼서 빠르다.)

물리 메모리를 직접 할당하기에 힙크기의 제약과는 무관하지만, 이 역시도 메모리다. 즉 `-Xmx`등의 매개 변수를 설정할 때 가상머신의 메모리 크기만 고려할 뿐, 다이렉트 메모리는 간과하는 경우가 종종 있다. 사용되는 모든 메모리 영역의 합이 물리 메모리 한계를 넘어서면 OOM이 발생한다.

> JVM 메모리 == 힙 + 스택 + 다이렉트 메모리 + 메서드 영역 + etc


### 2.3 핫스팟 가상 머신에서의 객체 들여다보기

책에선 핫스팟 가상 머신을 활용해 객체 생성과정을 설명한다.

#### 객체 생성

`new`키워드를 통해 객체를 생성할 수 있다. 이 과정은 클래스 로딩 후 객체를 담을 메모리를 할당한다. (객체에 필요한 메모리 크기는 클래스를 로딩하고 나면 완벽하게 알 수 있다.) 객체용 메모리 공간 할당은 자바 힙에서 특정 크기의 메모리 블록을 잘라 주는 일이라 할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/8343c150-d64b-411a-80df-f26a7069c5aa/image.png)

자바 힙이 규칙적이라면 위의 그림처럼 포인터 밀치기(bump the pointer)할당을 통해 할당된다. 

![](https://velog.velcdn.com/images/cksgodl/post/688d635b-7357-48d5-ae71-66509350abed/image.png)

하지만 보통 자바 힙은 규칙적이지 않으며, 중간 여유 세그먼트가 발생하게 된다. 따라서 가상 머신은 가용 메모리블록들을 목록으로 관리하며 객체 인스턴스를 담기에 충분한 공간을 찾아 할당한 후 목록을 갱신한다. __이 할당방식을 여유 목록(free list)라고 한다.__

> 관련하여 OS에서 메모리를 페이징하여 관리하는 것과 비슷한 원리로 작동한다고 보면 된다.

멀티 쓰레딩 환경에서 여유 메모리의 시작 포인터 위치를 수정하는 것은 단순하지 않고, 쓰레드에 안전하지도 않다. 따라서 가용 공간을 어떻게 활용할지에 대해 몇가지 해법이 있다.

1. 메모리 할당 동기화

비교 및 교환(CAS)과 실패 시 재시도 방식을 가상 멋니이 원자적으로 수행하는 방식이다.

2. 스레드마다 다른 메모리 공간 할당.

스레드 각각이 자바힙 내에 작은 크기의 전용 메모리를 미리 할당 받는다. 이런 메모리를 쓰레드 로컬 할당 버퍼(TLAB)라고 한다. 각 쓰레드는 로컬 버퍼에서 메모리를 할당받아 사용하다. 버퍼가 부족해지면 그 때 동기화를 통해 새로운 버퍼를 할당받는다. JVM이 어떤 스레드 로컬 할당 버퍼를 사용할지는 `-XX:+/-UseTLAB` 매개 변수로 설정한다.

![](https://velog.velcdn.com/images/cksgodl/post/26f20050-ba4c-41bf-af93-9f70b2a94be0/image.png)

해당 TLAB내용은 GC와 이어진다.(3장)

> 참고) 각 클래스의 hashcode정보는 GC 세대 나이, TLAB 등의 상태에 따라 달라진다. 

---

위의 과정을 통해 메모리에 객체 인스턴스를 할당하였다. 이제 JVM은 class의 init메소드를 실행한다. (init()메소드까지 실행되어야 개발자의 의도대로 비로소 사용 가능한 진짜 객체가 완성된다.)

> 자바 컴파일러는 new키워드를 발견하면 바이트코드 명령어인 new와 invokespecial로 변환한다. new는 앞서 이야기한 메모리 할당을 의미하며, invokespcial은 init()메소드 호출을 담당한다. (new가 아닌 다른 방식으로 객체가 생성되면 init()이 실행되지 않을 수 있다.)

### 객체의 메모리 레이아웃

핫스팟 JVM에서는 다음과 같이 객체를 세 부분으로 나누어 힙에 저장한다. 

- 객체 헤더
  - 마크 워드 : 객체의 런타임 데이터(해시코드, GC세대 나이, 락 정보)
  - 클래스 워드(klass word) : 클래스 포인터로 메타스페이스를 나타낸다.
  - 배열 길이 : 배열객체일 경우
- 인스턴스 데이터 : 객체가 실제로 담고 있는 정보(필드, 함수)
- 정렬 패딩 : 전체 크기가 8바이트의 정수배가 되도록 자리 확보

#### 객체 헤더

- 해시코드
- GC 세대 나이
- 락 플래크
- 쓰레드가 점유하고 있는 락
- 쓰레드 아이디, 타임스탬프

등의 정보를 저장한다. 그리고 클래스 워드(klass word)를 저장하기도 하는데(JVM마다 다름) 이는 객체의 클래스 관련 메타데이터를 가리킨다.

> klass는 JVM이 런타임에 자바 클래스를 다루는 데 필요한 각종 정보(정의된 필드와 메서드 등)이 담겨있는 데이터 구조를 의미한다.

+) 배열이면 배열 길이도 저장한다.

#### 인스턴스 데이터

객체가 실제로 담고 있는 정보를 저장한다. (필드, 부모 클래스 유무, 오버라이드된 필드 등) 

이러한 정보의 저장 순서는 JVM의 할당 전략 매게 변수(`-XX:FieldsAllocationStyle`)와 자바 소스 코드에서 필드 선언 순서에 따라 달라진다. 

long, int, short, byte등 다양한 타입이 있고, 길이(크기)가 같은 필드들은 항상 같이 할당되고 저장된다.

추가로 `+XX:CompactFields`매개변수를 `true`로 설정하면 하위 클래스의 필드 중 길이가 짧은 것들은 상위 클래스 변수 사이사이에 끼워져서 공간이 조금 절약된다.

#### 정렬 패딩

이부분은 존재하지 않을 수 있으며 특별한 의미 없이 자리만을 확보한다. (객체의 시작 주소는 8바이트 정수배여야하기 떄문에) 이를 채우기위해 활용된다.

### 객체에 접근하기

대다수의 객체는 다른 객체 여러 개를 참조하여 만들어진다. JVM마다 객체 내 참조 객체에 접근하는 방법이 다르며, 주로 핸들이나 다이렉트 포인터를 사용한다.


#### 핸들 방식

![](https://velog.velcdn.com/images/cksgodl/post/c0b100d6-79d2-48f7-a87d-212140f76db4/image.png)

자바 힙에 핸들 저장용 풀이 별도로 존재하며, 참조에는 객체의 핸들 주소가 저장되고 핸들에는 다시 해당 객체의 인스턴스 데이터, 타입데이터, 구조 등의 정확한 주소 정보가 담길 것이다.

이런 방식은 안정적이다. GC중 객체의 위치가 바뀌는 상황에서도 참조 자체에는 손댈 필요가 없다. 그 대신 핸들내의 인스턴스 데이터 포인터만 변경하면 된다.

![](https://velog.velcdn.com/images/cksgodl/post/f3a3c1d1-afb4-4ec6-bad8-d63e988b8bb2/image.png)

다이렉트 포인트 방식에서는 자바 힙에 위치한 객체에서 인스턴스 데이터뿐 아니라 타입 데이터에 접근하는 길도 제공해야 한다. (스택의 참조에는 객체의 실제 주소가 바로 저장되어 있다.) 따라서 빠르다.

---

## 요약

### 1. 자바 메모리 관리 개요
- C, C++ 개발자는 메모리 관리를 수동으로 해야 하지만, 자바 개발자는 JVM의 자동 메모리 관리 덕분에 메모리 할당과 해제를 신경 쓰지 않아도 된다.
- JVM의 메모리 관리 메커니즘을 이해하지 못하면 문제가 발생했을 때 대처하기 어렵다.

### 2. JVM의 런타임 데이터 영역

#### PC(program counter)
- 스레드별로 존재하는 작은 메모리 영역.
- 현재 실행 중인 스레드의 다음 실행할 바이트코드 줄 번호를 저장한다.
- 각 스레드는 독립된 PC를 가진다.

#### 스택(Stack memory)
- 스레드 프라이빗 영역.
- 각 메서드 호출 시 스택 프레임을 생성하여 지역 변수, 피연산자 스택, 동적 링크 등을 저장.
- 스택 깊이가 허용치를 넘으면 `StackOverflowError`, 여유 메모리가 부족하면 `OutOfMemoryError`.

#### 네이티브 메서드 스택
- 실제 기계어로 작성된 프로그램을 실행.
- 스택 오버플로와 메모리 부족 에러 발생 가능.

#### 자바 힙(Java heap)
- 모든 스레드가 공유하는 가장 큰 메모리 영역.
- 객체 인스턴스를 저장.
- 가비지 컬렉터가 관리.
- 힙 메모리 부족 시 GC가 일어나고, 이를 통해 확장할 수 없으면 `OutOfMemoryError`.

#### 메서드 영역(Method Area)
- 모든 스레드가 공유.
- 타입 정보, 상수, 정적 변수, JIT 컴파일 코드 캐시를 저장.

#### 런타임 상수 풀
- 메서드 영역의 일부.
- 클래스 파일의 상수, 리터럴, 심벌 참조를 저장.

#### 다이렉트 메모리
- JVM 외부에서 관리.
- 네이티브 메서드를 통해 DirectByteBuffer 객체를 사용하여 빠른 데이터 작업 가능.
- 물리 메모리 한계를 넘으면 `OutOfMemoryError`.

### 3. 핫스팟 가상 머신에서의 객체 생성 및 메모리 레이아웃

#### 객체 생성
- `new` 키워드로 객체 생성.
- 클래스 로딩 후 객체 메모리를 할당.
- 메모리 할당 방식: 포인터 밀치기(bump the pointer) 또는 여유 목록(free list).

#### 객체의 메모리 레이아웃
- **객체 헤더**: 마크 워드, 클래스 워드, 배열 길이 정보.
- **인스턴스 데이터**: 실제 객체의 필드 정보.
- **정렬 패딩**: 8바이트 정수 배수로 맞추기 위한 공간.

#### 객체에 접근하기
- **핸들 방식**: 핸들 저장용 풀에서 객체의 인스턴스 데이터와 타입 데이터에 접근.
- **다이렉트 포인트 방식**: 객체의 실제 주소를 바로 참조하여 빠르게 접근.









