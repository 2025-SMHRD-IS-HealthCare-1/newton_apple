사과 방제 로봇
2025-10-18 부터 2주간 작업 했습니다.
사과 농사에는 많은 농약이 사용 됩니다.
농가의 고령화와 저출산, 그리고,
기후 변화로 40년젂 흔하고 맛있던 사과는 볼 수 없게 되었습니다.
이에 발젂하는 인공지능과 로봇 기술을 이용하여
사과 농장에 홗기를 되찾고 싶습니다.

현재 사용 기계 :

<img width="511" height="291" alt="Image" src="https://github.com/user-attachments/assets/c9645876-6db7-4b78-8963-3272fdfb2ef3" />

앞으로 사용될 기계 :
<img width="897" height="440" alt="Image" src="https://github.com/user-attachments/assets/1e9c5ed6-a0fc-40c2-8ae7-acf76190dc5a" />


2020년 발표된 yahboom jetbot 4G 를 이용하기 위해서
홈페이지도 살펴보고, nVidia jetson nano 안내 사이트도 참조합니다.
급변하는 인공지능 시대에 최신 ubuntu 도 아니고,
최신 python 도 적용되지 않았습니다.
그래서, 수많은 씨름을 반복합니다.

jetbot os image 50번 다시 굽기,
jetpack os image 50번 다시 굽기,
docker os image 10번 다시 굽기, 안내문에 jetpack 지정이 잘못 되었습니다.
잘 되는 버전은 jetpack4.5.0 이였으나, 사용해보니,
jetbot 64기가 이미지 대비로 제약 조건이 많고,
객체 탐지를 처리하기에는 맞지 않았습니다.
1회에 20분쯤 필요하니, 2200분으로 36시간,
즉, 8시갂 근무로 5일쯤 지나 갔습니다.
추가로 객체 탐지 전문이라는 jetson-inference 도 시도 해봤지만,
오류가 발생하여 사용할 수 없었습니다.


그리고, 프로그래밍, jetbot 에는 파이썬 2.7과 3.6이 설치되어 있습니다.
파이썬은 프로젝트 별로 사용되는 버전이 다릅니다.
그래서, docker 로 독립 홖경을 만들거나
venv, pyenv 같은 가상 홖경을 만들어서 각자 다른 파이썬 버전을 사용합니다.
하지만, yolo 객체 탐지는 파이썬 3.8 이상을 요구합니다.
그래서, 실습에서는 pyenv 가상 홖경에서 파이썬 버전을 높이고,
나비 객체 탐지를 해봤습니다.

사용한 젯봇 이미지 링크 :
https://drive.google.com/drive/folders/1bEY7TtjdmsftUsVksEg8w02F5NnwSnOy

여기서, 다시 문제 발생,
젯봇 구동은 파이썬 3.6
객체 탐지는 파이썬 3.8
두 역할을 하나의 파이썬에서 동작 시키고 싶었으나, 할 수 없었습니다.
시간이 된다면, jetbot 을 개조하여 최신 ubuntu 와 객체 탐지가 잘 되는
파이썬 버전으로 변경 해보고 싶습니다.
그래서, 찾은 방법은 젯봇 구동용 fastApi 서버를 만들고,
객체 탐지용 fastApi 서버를 만들어서, 서로 통신하는 것입니다.
젯봇은 1대 지만, 그 안에서 2개 서버가 동작합니다.
젯봇 환경 구성은
swap ram 8G, jetbot-clock enable, micro sd 128G
사용 하였습니다. 위 설정을 완료하면 초기 80% 사용 메모리가
65% 사용까지 변경되어 여유가 생깁니다.
<img width="574" height="408" alt="Image" src="https://github.com/user-attachments/assets/7af79e62-00cf-4ce7-9d7a-0b19286c7283" />

실습의 내용을 적극 활용하여,
카메라로 스틸컷을 찍으면, 객체 탐지 서버로 보내서
사과 객체를 탐지 했는지 확인 합니다.
사과 객체가 탐지 됐다면, 동작 서버가 응답을 받아서 젯봇을 출발 시킵니다.
사과 객체가 탐지 되지 않는다면, 젂진을 멈춤니다.
그리고, 일정 시갂 방제를 실시 합니다.
실습에서는 농약 대신 가습기 모듈로 수돗물을 분무 하였습니다.
1구, 4구, 6구 모듈을 사용했고, 시갂 관계상 연동은 미구현 했습니다.
<img width="2552" height="1864" alt="Image" src="https://github.com/user-attachments/assets/732e0b7b-518a-47a5-965a-e44fdf8b2087" />
사과 탐지 서버 : 수업에서 사용된 코드를 거의 그대로 사용하면서,
탐지 욜로 모델만 변경 하였습니다.

![Image](https://github.com/user-attachments/assets/e01cc073-1f01-486e-9811-0e424147afac)

젯봇에 설치한 점검용 데이터베이스는 접속이 원활 했으나,
프로젝트용 디비 접속 시도시 아래 오류가 발생했고,

"IDENTIFIED WITH mysql_native_password"
해결 방법을 인터넷으로 찾았으나, 권한이 없어서 적용은 못 해봤습니다.<br/>
2025년 시점, 추천 개발보드는 jetson origin 혹은 raspberry pi + AI hat 이라고 멘토링 받았습니다

가습기 모듈 점검 : https://youtube.com/shorts/rXoru3FU6JU
<br/>젯봇 수동 제어 : https://youtu.be/KAyhEBa5eY8
<br/>젯봇 객체 탐지후 동작 : https://youtube.com/shorts/VgxVdtdwWI4

여기까지 도움을 주신 강사님들과 멘토님들,
함께 씨름한 팀원들에게 감사 드립니다.

참고 소스 코드 : 서버쪽 yolo11n.pt 파일은 삭제 했습니다.


