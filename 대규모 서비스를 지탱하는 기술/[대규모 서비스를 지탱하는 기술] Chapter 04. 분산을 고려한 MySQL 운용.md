## 목차

- [인덱스를 올바르게 운용하기](#인덱스를-올바르게-운용하기)

- [mysql의 분산](#mysql의-분산)

- [mysql의 스케일아웃과 파티셔닝](#mysql의-스케일아웃과-파티셔닝)

# 분산을 고려한 MySQL 운용

분산을 고려한 `MySQL` 운용의 포인트는 다음과 같습니다.

- OS 캐시 활용
- 인덱스를 적절하게 설정하기
- 확장을 전제로 한 설계

> `OS` 캐시 활용

`RDB`에서의 스키마를 설계할 때 데이터 크기에 미치는 영향을 고려해야 합니다. 3억개의 데이터라면 8byte 칼럼만 추가해도 약 3기가정도의 용량을 차지하게 됩니다.

또한 `데이터량 < 물리 메모리` 를 유지하라고 합니다. -> 이게 되나..?

> 인덱스가 무엇일까요?

인덱스란 추가적인 쓰기 작업과 저장 공간을 활용하여 데이터베이스 테이블의 검색 속도를 향상시키기 위한 자료구조를 의미합니다.

> 정규화를 활용하라

정규화를 통해 데이터베이스의 중복을 없애는 것 만으로 캐시 적중률을 높일 수 있을 뿐 더러, 파티셔닝을 수행할 때 도움이 될 수 있습니다.

하지만 쿼리가 복잡해져서 속도가 떨어지는 경우가 있음으로 속도와 데이터 크기 간 상반관계를 생각해야 합니다.

## 인덱스를 올바르게 운용하기

알고리즘, 데이터 구조에서 탐색을 할 때는 기본적으로 트리가 널리 사용됩니다. 인덱스는 주로 탐색을 빠르게 하기 위한 것으로, 그 내부 데이터 구조로 트리가 사용됩니다.

`MYSQL`의 인덱스는 기본저긍로 `B+`트리라는 데이터 구조를 활용합니다. 이는 데이터를 열심히 추가해도 아이템 `n`개당 높이가 `log(n)`이 유지되는 트리를 의미합니다.

`MySQL`에서 인덱스를 만들면 `B`트리의 변종인 `B+`트리에 의한 트리 데이터 구조가 생깁니다. 해당 트리는 해당 인덱스에 대한 조건으로 이루어진 트리임으로 검색이 매우 빠릅니다.

### 인덱스의 효과

실제 인덱스의 효과를 측정해보았습니다.

`4_000`만 건 태그 테이블에서의 탐색

- 인덱스 없음 = 선형탐색
  - O(n) 최대 `4_000`만 번 탐색
- 인덱스 있음 = 이분탐색
  - O(log n) 최대 25.25번 탐색

> 힘의 차이가 느껴지십니까?

이를 활용하면 계산량 측면에서 개선될 뿐만 아니라, 디스크 구조에 최적화된 인덱스를 사용해서 탐색함으로써 디스크 `Seek`횟수면에서도 개선됩니다.

> 인덱스 만능주의인것 처럼 이야기를 하였지만, 인덱스에 대한 `B+`를 구성해야 함으로 이도 상당한 용량을 차지할 수 있습니다. 인덱스 관련하여 데이터를 추가하거나 수정할 때는 `DBA`분들과 이야기하는 것이 필수

+) 인덱스의 작용

`MySQL`의 인덱스 사양에는 약간의 특성이 있는데, 인덱스를 걸어놓고 있는 칼럼을 대상으로 한 쿼리라도 `SQL`에 따라서 그것이 사용되거나 사용되지 않기도 합니다.

이게 무슨 뜻이야??

```sql
SELECT * FROM entry WHERE url = 'asdasd`
```

은 `Where`절에 `url`칼럼을 지정하고 있습니다. 따라서 `url`칼럼에 인덱스가 걸려 있다면 사용됩니다.

기본적으로 인덱스가 사용되는 것은

- `WHERE`
- `ORDER BY`
- `GROUP BY`

의 조건에 지정된 칼럼들이 사용됩니다.

```sql
SELECT * FROM entry WHERE url
LIKE 'http://hatena.%'
ORDER BY timestamp
```

다음과 같은 쿼리문을 던지면 `url`의 인덱스를 통해 고속으로 검색하고, `timestamp`를 활용해 고속으로 정렬되는 것을 기대하겠지만 실상은 그렇지 않습니다.

이 경우는 어느 한쪽의 인덱스만 사용됩니다. 즉, 검색이나 정렬 중 어느 한쪽은 인덱스를 사용하지 않는 처리로 수행됩니다.

그 이유로는 `MySQL`은 한 번의 쿼리에서 하나의 인덱스만 사용한다는 특성을 갖고 있는 것이 그 특징입니다. 위의 쿼리에서 양쪽의 인덱스를 태우고자 한다면 `(url, timestamp)`를 쌍으로 한 복합 인덱스를 설정할 필요가 있습니다.

### 인덱스가 작용하는지 확인하는 법

`SQL`에는 `explain`이라는 명령어가 있습니다. 이는 인덱스가 작용하고 있는지 여부를 조사해 줍니다.

```sql
EXPLAIN SELECT url FROM entry WHERE eid = <EntryID>
```

와 같은 형식으로 입력한다면, 인덱스 키, 조사한 행의 갯수 등을 표시해 줍니다.

## MySQL의 분산

### `MySQL`의 레플리케이션 기능

`MySQL`의 분산은 어떻게 실현할 것인가?에 대해 알아 봅시다.

> `MySQL`에는 레플리케이션(Replication)기능이 존재합니다. 이는 마스터를 정하고 마스터를 뒤따르는 슬레이브를 정하여 마스터에 쓴 내용을 슬레이브가 폴링해서 동일한 내용으로 자신을 갱신하는 것을 의미합니다.

이렇게 하여 동일한 내용의 서버를 여러 대 마련할 수 있습니다.

마스터/슬레이브로 레플리케이션해서 서버를 여러 대 준비하게 되면 서버에서는 로드밸런서를 경유해서 슬레이브로 질의합니다. 이에 따라 쿼리를 여러 서버로 분산시킬 수 있습니다.

그래도 동기화에 대한 문제점은 생기게 됩니다. 따라서 어플리케이션의 구현단에서 `SELECT`등 참조 쿼리만 로드밸런서로 흘러가도록 하고, 갱신 쿼리는 마스터로 직접 던지게 할 수 있습니다. (갱신 쿼리를 슬레이브로 던지면 슬레이브와 마스터 간 내용을 동기화 할 수 없습니다.)

### 마스터/슬레이브의 특징

그렇다면 `마스터는 어떻게 분산할 것인가?`에 대해 고민해봐야 합니다.

참고로 웹 어플리케이션에서의 `90%`이상이 참조계열의 쿼리입니다. 쓰기는 상대적으로 훨씬 적습니다. 따라 마스터의 부하는 그렇게 크지 않지만, 마스터가 업데이트되면 모든 슬레이브가 업데이트 되어아하며, 잦은 업데이트가 있다면 슬레이브 서버는 급격히 느려지게 될 것 입니다.

이를 해결하기 위해서 테이블을 분리하여 테이블의 크기를 작게하는 방법이 있을 수도 있으며, 동일 호스트 내에서 여러 디스크를 가지고 분산할 수도 있으며, 다른 서버로 분산할 수도 있습니다.

또 다른 해결법으로 `RDBMS`를 사용하지 않는 방법도 있습니다. 저자는 `Tokyo Tyrant`라는 `key-value`형식의 데이터베이스를 활용한다고 하고, 오늘날은 대표적으로 `Redis`를 활용할 수 있을 것입니다. 이는 오버헤드도 적고 압도적으로 빠르며 확장하기 쉽습니다.

## MySQL의 스케일아웃과 파티셔닝

### MySQL의 스케일아웃 전략

> `MySQL`의 기본적인 스케일 아웃 전략으로는 데이터가 메모리에 올라가는 크기이면 메모리에 올리고, 올라가지 않으면 메모리를 증설하는 것이였습니다. 그리고 가장 중요한 것은 `인덱스는 제대로 걸자`였습니다.

하지만 메모리 증설이 불가능하면 파티셔닝을 고려할 수 있습니다.

### 파티셔닝에 대한 보충

파티셔닝이란 `테이블A`와 `테이블B`를 서로 다른 서버에 놓아서 분산하는 방법을 의미합니다. 이는 국소성을 활용해서 분산할 수 있으므로 캐시가 유효하기에 효과적입니다.

### 파티셔닝을 전제로 한 설계

`MySQL`에는 서로 다른 서버에 있는 테이블을 `JOIN`하는 기능이 기본적으로는 없습니다.(MySQL 5.1에서는 FEDERATED 테이블을 활용하면 가능) 두개의 테이블을 조인하기 위해서는 서로 다른 두 서버에 쿼리를 2번 날려야 합니다.

따라서 기본적으로는 `JOIN`쿼리는 대상이 되는 테이블을 앞으로도 서버 분할하지 않을 것이라고 보장할 수 있을때에만 사용합니다.

이에따라 `JOIN`이라는 명령 자체를 수행하기 보단 2번의 쿼리와 `WHERE IN`을 활용해 데이터를 뽑아내는 것을 권장합니다.

- `JOIN` 사용 쿼리

```sql
SELECT url FROM entry
INNER JOIN bookmark ON entry.eid = bookmark.eid
WHERE bookmark.uid = 169848 LIMIT 5;
```

- `WHERE IN` 사용 쿼리

```sql
SELECT eid FROM bookmark
WHERE bookmark.uid = 169848 LIMIT 5;
// Result : [0, 4, 5, 6, 7]

SELECT URL FROM entry
WHERE eid IN =  (0, 4, 5, 6, 7);
```

### 파티셔닝의 상반관계

파티셔닝의 좋은 점은 부하가 내려가고 국소성이 늘어나서 캐시 효과가 높아진다는 점입니다. 그렇다면 나쁜 점은 무엇일까요?

> 운용이 복잡해 진다.

어디에 어떤 `DB`가 있는 파악하는게 매우 힘듭니다.

더해 현재 다니고 있는 회사의 경우는 도메인 용어까지 같이 데이터베이스에 섞여있기에 초반에는 데이터베이스 구조를 이해하기 아주 힘들었습니다.

> 고장률이 높아집니다.

대수가 늘어나는 만큼 고장확률이 높아집니다. 이전까지 1대였던 서버를 분할하게 되면 서버가 4대 더 생성되게 되고, 이를 분할하는 경우는 8대가 되게 됩니다.

- 왜 4대씩 서버가 늘어나나요?

  - 마스터 1대, 슬레이브 3대로 파티셔닝을 구성하기 때문입니다.

  - 그 이유로는 마스터 1대 슬레이브 2대로 구성했을 때 슬레이브 한대가 고장났을 때, 고장난 슬레이브를 고치고, 남은 슬레이브 하나가 복사작업과 조회작업을 동시에 수행해야 하는데 이는 불가능에 가깝기 때문에 서비스가 멈추게 됩니다. 따라서 보통 파티셔닝은 4대를 한 세트로 생각할 수 있습니다.

파티셔닝을 활용하면 장점으로

- 부하가 내려가고
- 국소성이 증가함으로 캐시 효과가 높아집니다.

단점으로는

- 운용이 복잡해지고 고장확률이 올라갑니다.
- 운용이 복잡해지면 경제적 비용이 듭니다.
- 메모리를 사야합니다.(서버)

## 정리

- 캐시가 중요하고 메모리가 디스크보다 빠릅니다.

- 조회할 떄는 적절한 인덱스를 태웁시다.

- 분산을 위해 파티셔닝을 활용할 수도 있지만, 국소성 및 운용 복잡도를 고려하세요.
