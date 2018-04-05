-- 제갈용오, 이근혁 -- 
--    2018/04/04    --
-- 테이블  스크립트 --

CREATE TABLE crawler (
    _id INT(10) NOT NULL PRIMARY KEY,          -- 게시글 ID
    filename VARCHAR(200) NOT NULL,             -- 파일명
    path VARCHAR(100) NOT NULL,                -- 파일 경로
    license VARCHAR(50) NOT NULL,              -- 라이선스 이미지 파일명 
    uci VARCHAR(30),                           -- UCI (고유번호) 
    icn VARCHAR(30),                           -- ICN (고유번호)
    author VARCHAR(100),                       -- 저작자
    public_author VARCHAR(100),                -- 공동저작자
    publicate_date VARCHAR(12),                -- 공표일자(년도)
    create_date VARCHAR(12),                   -- 창작일자(년도)
    publicate_contry VARCHAR(20),              -- 공표국가
    classification VARCHAR(30),                -- 분류(장르)
    original_text VARCHAR(200),                 -- 원문제공
    summary_info VARCHAR(500),                 -- 요약정보
    relation_tag VARCHAR(200),                 -- 관련태그
    publisher VARCHAR(50),                     -- 발행자
    contributor VARCHAR(50),                   -- 기여자
    alternate_title VARCHAR(200),              -- 저작물명 대체제목
    substitute VARCHAR(100),                   -- 저작물 파일유형
    attribute VARCHAR(30),                     -- 저작물 속성
    collect_type VARCHAR(10),                  -- 수집연계유형
    collect_target VARCHAR(30),                -- 수집연계대상명
    collect_url VARCHAR(30),                   -- 수집연계URL
    main_language VARCHAR(10),                 -- 주언어
    original_type VARCHAR(10),                 -- 원저작물유형
    original_date VARCHAR(12),                 -- 원저작물창작일
    original_size VARCHAR(30),                 -- 원저작물크기
    original_collection VARCHAR(30),           -- 원저작물소장처
    col_size INT(10)                           -- 컬럼 개수
);

