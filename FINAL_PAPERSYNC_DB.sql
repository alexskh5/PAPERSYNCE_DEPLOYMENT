PGDMP  8    $                }            DB_PAPERSYNC    17.5 (Homebrew)    17.0 t               0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false                       0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false                       0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false                       1262    74010    DB_PAPERSYNC    DATABASE     p   CREATE DATABASE "DB_PAPERSYNC" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C';
    DROP DATABASE "DB_PAPERSYNC";
                     postgres    false            �            1255    74546    communication_doc_history()    FUNCTION     U  CREATE FUNCTION public.communication_doc_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    action_type TEXT;
    row_title TEXT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        action_type := 'Created';
        row_title := NEW.comm_title;
    ELSIF TG_OP = 'UPDATE' THEN
        action_type := 'Updated';
        row_title := NEW.comm_title;
    ELSIF TG_OP = 'DELETE' THEN
        action_type := 'Deleted';
        row_title := OLD.comm_title;
    END IF;

    INSERT INTO history(table_name, row_title, staff_id, action_detail, action_date)
    VALUES (
        'COMMUNICATION_DOC',
        row_title,
        COALESCE(NEW.updated_by, OLD.updated_by, NEW.created_by),  -- ✅ Changed here
        action_type || ' communication document: ' || COALESCE(row_title, 'No Title'),
        CURRENT_TIMESTAMP
    );

    RETURN NULL;
END;
$$;
 2   DROP FUNCTION public.communication_doc_history();
       public               postgres    false            �            1255    74585    log_motivation_changes()    FUNCTION     }  CREATE FUNCTION public.log_motivation_changes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO history(table_name, row_title, staff_id, action_detail)
    VALUES (
        'motivation_board',
        'Motivation Board',
        NEW.last_updated_by,
        'Updated motivation text: ' || LEFT(NEW.motivation_text, 50) || '...'
    );
    RETURN NEW;
END;
$$;
 /   DROP FUNCTION public.log_motivation_changes();
       public               postgres    false            �            1255    74540    log_propose_measure_changes()    FUNCTION     Z  CREATE FUNCTION public.log_propose_measure_changes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    action_text TEXT;
    changes TEXT := '';
BEGIN
    IF TG_OP = 'INSERT' THEN
        action_text := 'Created propose measure: ' || NEW.PROPOSE_TITLE;
        
    ELSIF TG_OP = 'UPDATE' THEN
        action_text := 'Updated propose measure: ' || NEW.PROPOSE_TITLE;
        
        -- Detect specific changes
        IF NEW.PROPOSE_TITLE <> OLD.PROPOSE_TITLE THEN
            changes := changes || 'Title changed from "' || OLD.PROPOSE_TITLE || '" to "' || NEW.PROPOSE_TITLE || '". ';
        END IF;
        
        IF NEW.COND_ID <> OLD.COND_ID THEN
            SELECT 'Status changed from ' || old_cond.COND_NAME || ' to ' || new_cond.COND_NAME || '. '
            INTO changes
            FROM CONDITION_TYPE old_cond, CONDITION_TYPE new_cond
            WHERE old_cond.COND_ID = OLD.COND_ID AND new_cond.COND_ID = NEW.COND_ID;
        END IF;
        
        -- Add more field comparisons as needed
        
        IF changes <> '' THEN
            action_text := action_text || ' Changes: ' || changes;
        END IF;
        
    ELSIF TG_OP = 'DELETE' THEN
        action_text := 'Deleted propose measure: ' || OLD.PROPOSE_TITLE;
    END IF;
    
    INSERT INTO HISTORY (TABLE_NAME, ROW_TITLE, STAFF_ID, ACTION_DETAIL)
    VALUES (
        'PROPOSE_MEASURE', 
        COALESCE(NEW.PROPOSE_TITLE, OLD.PROPOSE_TITLE), 
        COALESCE(NEW.updated_by, OLD.updated_by, NEW.created_by, OLD.created_by), 
        action_text
    );
    
    RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END;
$$;
 4   DROP FUNCTION public.log_propose_measure_changes();
       public               postgres    false                       1255    74542    minutes_history()    FUNCTION     0  CREATE FUNCTION public.minutes_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    action_type TEXT;
    row_title TEXT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        action_type := 'Created';
        row_title := NEW.min_num;
    ELSIF TG_OP = 'UPDATE' THEN
        action_type := 'Updated';
        row_title := NEW.min_num;
    ELSIF TG_OP = 'DELETE' THEN
        action_type := 'Deleted';
        row_title := OLD.min_num;
    END IF;

    INSERT INTO history(table_name, row_title, staff_id, action_detail, action_date)
    VALUES (
        'MINUTES',
        row_title,
        COALESCE(NEW.updated_by, OLD.updated_by, NEW.created_by),  -- ✅ Updated here
        action_type || ' minutes record: ' || COALESCE(row_title, 'No Title'),
        CURRENT_TIMESTAMP
    );

    RETURN NULL;
END;
$$;
 (   DROP FUNCTION public.minutes_history();
       public               postgres    false            �            1255    74553    move_to_trash()    FUNCTION     X  CREATE FUNCTION public.move_to_trash() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO trash_bin (
        table_name, 
        record_id, 
        deleted_data,
        deleted_by
    ) VALUES (
        TG_TABLE_NAME,
        OLD.propose_id,
        to_jsonb(OLD),
        OLD.updated_by  
    );
    RETURN OLD;
END;
$$;
 &   DROP FUNCTION public.move_to_trash();
       public               postgres    false                        1255    74544    other_doc_history()    FUNCTION     @  CREATE FUNCTION public.other_doc_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    action_type TEXT;
    row_title TEXT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        action_type := 'Created';
        row_title := NEW.other_title;
    ELSIF TG_OP = 'UPDATE' THEN
        action_type := 'Updated';
        row_title := NEW.other_title;
    ELSIF TG_OP = 'DELETE' THEN
        action_type := 'Deleted';
        row_title := OLD.other_title;
    END IF;

    INSERT INTO history(table_name, row_title, staff_id, action_detail, action_date)
    VALUES (
        'OTHER_DOC',
        row_title,
        COALESCE(NEW.updated_by, OLD.updated_by, NEW.created_by),  -- ✅ Updated here
        action_type || ' other document: ' || COALESCE(row_title, 'No Title'),
        CURRENT_TIMESTAMP
    );

    RETURN NULL;
END;
$$;
 *   DROP FUNCTION public.other_doc_history();
       public               postgres    false            �            1259    74483    communication_doc    TABLE     �  CREATE TABLE public.communication_doc (
    comm_id integer NOT NULL,
    comm_date_rcvd date NOT NULL,
    comm_title text NOT NULL,
    comm_venue text,
    comm_remarks text,
    comm_attachfile text,
    comm_is_liquidate boolean DEFAULT false,
    created_by integer NOT NULL,
    updated_by integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
 %   DROP TABLE public.communication_doc;
       public         heap r       postgres    false            �            1259    74482    communication_doc_comm_id_seq    SEQUENCE     �   CREATE SEQUENCE public.communication_doc_comm_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.communication_doc_comm_id_seq;
       public               postgres    false    232                       0    0    communication_doc_comm_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.communication_doc_comm_id_seq OWNED BY public.communication_doc.comm_id;
          public               postgres    false    231            �            1259    74023    condition_type    TABLE     s   CREATE TABLE public.condition_type (
    cond_id integer NOT NULL,
    cond_name character varying(50) NOT NULL
);
 "   DROP TABLE public.condition_type;
       public         heap r       postgres    false            �            1259    74022    condition_type_cond_id_seq    SEQUENCE     �   CREATE SEQUENCE public.condition_type_cond_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.condition_type_cond_id_seq;
       public               postgres    false    220                       0    0    condition_type_cond_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.condition_type_cond_id_seq OWNED BY public.condition_type.cond_id;
          public               postgres    false    219            �            1259    74526    history    TABLE       CREATE TABLE public.history (
    history_id integer NOT NULL,
    table_name character varying(50) NOT NULL,
    row_title text NOT NULL,
    staff_id integer,
    action_detail text NOT NULL,
    action_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.history;
       public         heap r       postgres    false            �            1259    74525    history_history_id_seq    SEQUENCE     �   CREATE SEQUENCE public.history_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.history_history_id_seq;
       public               postgres    false    236                       0    0    history_history_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.history_history_id_seq OWNED BY public.history.history_id;
          public               postgres    false    235            �            1259    74227    minutes    TABLE     �  CREATE TABLE public.minutes (
    min_id integer NOT NULL,
    min_date date,
    min_link character varying(500),
    type_id integer,
    sub_id integer,
    created_by integer NOT NULL,
    updated_by integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    min_series_yr date,
    min_num text
);
    DROP TABLE public.minutes;
       public         heap r       postgres    false            �            1259    74226    minutes_min_id_seq    SEQUENCE     �   CREATE SEQUENCE public.minutes_min_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.minutes_min_id_seq;
       public               postgres    false    230                       0    0    minutes_min_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.minutes_min_id_seq OWNED BY public.minutes.min_id;
          public               postgres    false    229            �            1259    74220    minutes_subtype    TABLE     r   CREATE TABLE public.minutes_subtype (
    sub_id integer NOT NULL,
    sub_name character varying(50) NOT NULL
);
 #   DROP TABLE public.minutes_subtype;
       public         heap r       postgres    false            �            1259    74219    minutes_subtype_sub_id_seq    SEQUENCE     �   CREATE SEQUENCE public.minutes_subtype_sub_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.minutes_subtype_sub_id_seq;
       public               postgres    false    228                       0    0    minutes_subtype_sub_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.minutes_subtype_sub_id_seq OWNED BY public.minutes_subtype.sub_id;
          public               postgres    false    227            �            1259    74213    minutes_type    TABLE     q   CREATE TABLE public.minutes_type (
    type_id integer NOT NULL,
    type_name character varying(50) NOT NULL
);
     DROP TABLE public.minutes_type;
       public         heap r       postgres    false            �            1259    74212    minutes_type_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.minutes_type_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.minutes_type_type_id_seq;
       public               postgres    false    226                       0    0    minutes_type_type_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.minutes_type_type_id_seq OWNED BY public.minutes_type.type_id;
          public               postgres    false    225            �            1259    74555    motivation_board    TABLE     �   CREATE TABLE public.motivation_board (
    motivation_id integer NOT NULL,
    motivation_text text NOT NULL,
    last_updated_by integer,
    last_updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
 $   DROP TABLE public.motivation_board;
       public         heap r       postgres    false            �            1259    74554 "   motivation_board_motivation_id_seq    SEQUENCE     �   CREATE SEQUENCE public.motivation_board_motivation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public.motivation_board_motivation_id_seq;
       public               postgres    false    238                       0    0 "   motivation_board_motivation_id_seq    SEQUENCE OWNED BY     i   ALTER SEQUENCE public.motivation_board_motivation_id_seq OWNED BY public.motivation_board.motivation_id;
          public               postgres    false    237            �            1259    74505 	   other_doc    TABLE     �  CREATE TABLE public.other_doc (
    other_id integer NOT NULL,
    other_date date NOT NULL,
    other_title text NOT NULL,
    other_from text,
    other_status text,
    other_attachfile text,
    created_by integer NOT NULL,
    updated_by integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.other_doc;
       public         heap r       postgres    false            �            1259    74504    other_doc_other_id_seq    SEQUENCE     �   CREATE SEQUENCE public.other_doc_other_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.other_doc_other_id_seq;
       public               postgres    false    234                       0    0    other_doc_other_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.other_doc_other_id_seq OWNED BY public.other_doc.other_id;
          public               postgres    false    233            �            1259    74030    propose_measure    TABLE     �  CREATE TABLE public.propose_measure (
    propose_id integer NOT NULL,
    propose_date_rcvd date NOT NULL,
    propose_title text NOT NULL,
    propose_rcvd_from text NOT NULL,
    remarks text,
    propose_attachfile text,
    propose_reso_number text,
    propose_ordi_number text,
    propose_session_date date,
    propose_author text,
    propose_is_scan boolean DEFAULT false,
    propose_is_furnish boolean DEFAULT false,
    propose_is_publication boolean DEFAULT false,
    propose_is_posting boolean DEFAULT false,
    cond_id integer,
    created_by integer NOT NULL,
    updated_by integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    series_yr date
);
 #   DROP TABLE public.propose_measure;
       public         heap r       postgres    false            �            1259    74029    propose_measure_propose_id_seq    SEQUENCE     �   CREATE SEQUENCE public.propose_measure_propose_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.propose_measure_propose_id_seq;
       public               postgres    false    222                       0    0    propose_measure_propose_id_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.propose_measure_propose_id_seq OWNED BY public.propose_measure.propose_id;
          public               postgres    false    221            �            1259    74012    staff    TABLE     5  CREATE TABLE public.staff (
    staff_id integer NOT NULL,
    staff_firstname character varying(255),
    staff_lastname character varying(255),
    staff_prof_pic text,
    staff_birthdate date,
    staff_address text,
    staff_username character varying(255) NOT NULL,
    staff_password text NOT NULL
);
    DROP TABLE public.staff;
       public         heap r       postgres    false            �            1259    74011    staff_staff_id_seq    SEQUENCE     �   CREATE SEQUENCE public.staff_staff_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.staff_staff_id_seq;
       public               postgres    false    218                       0    0    staff_staff_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.staff_staff_id_seq OWNED BY public.staff.staff_id;
          public               postgres    false    217            �            1259    74060 	   trash_bin    TABLE     �   CREATE TABLE public.trash_bin (
    trash_id integer NOT NULL,
    table_name text NOT NULL,
    record_id integer NOT NULL,
    deleted_data jsonb NOT NULL,
    deleted_at timestamp without time zone DEFAULT now() NOT NULL,
    deleted_by integer
);
    DROP TABLE public.trash_bin;
       public         heap r       postgres    false            �            1259    74059    trash_bin_trash_id_seq    SEQUENCE     �   CREATE SEQUENCE public.trash_bin_trash_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.trash_bin_trash_id_seq;
       public               postgres    false    224                       0    0    trash_bin_trash_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.trash_bin_trash_id_seq OWNED BY public.trash_bin.trash_id;
          public               postgres    false    223            �            1259    74570    user_accomplishments    TABLE        CREATE TABLE public.user_accomplishments (
    accomplishment_id integer NOT NULL,
    staff_id integer,
    accomplishment_text text NOT NULL,
    is_completed boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
 (   DROP TABLE public.user_accomplishments;
       public         heap r       postgres    false            �            1259    74569 *   user_accomplishments_accomplishment_id_seq    SEQUENCE     �   CREATE SEQUENCE public.user_accomplishments_accomplishment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 A   DROP SEQUENCE public.user_accomplishments_accomplishment_id_seq;
       public               postgres    false    240                        0    0 *   user_accomplishments_accomplishment_id_seq    SEQUENCE OWNED BY     y   ALTER SEQUENCE public.user_accomplishments_accomplishment_id_seq OWNED BY public.user_accomplishments.accomplishment_id;
          public               postgres    false    239            )           2604    74486    communication_doc comm_id    DEFAULT     �   ALTER TABLE ONLY public.communication_doc ALTER COLUMN comm_id SET DEFAULT nextval('public.communication_doc_comm_id_seq'::regclass);
 H   ALTER TABLE public.communication_doc ALTER COLUMN comm_id DROP DEFAULT;
       public               postgres    false    231    232    232                       2604    74026    condition_type cond_id    DEFAULT     �   ALTER TABLE ONLY public.condition_type ALTER COLUMN cond_id SET DEFAULT nextval('public.condition_type_cond_id_seq'::regclass);
 E   ALTER TABLE public.condition_type ALTER COLUMN cond_id DROP DEFAULT;
       public               postgres    false    220    219    220            0           2604    74529    history history_id    DEFAULT     x   ALTER TABLE ONLY public.history ALTER COLUMN history_id SET DEFAULT nextval('public.history_history_id_seq'::regclass);
 A   ALTER TABLE public.history ALTER COLUMN history_id DROP DEFAULT;
       public               postgres    false    236    235    236            &           2604    74230    minutes min_id    DEFAULT     p   ALTER TABLE ONLY public.minutes ALTER COLUMN min_id SET DEFAULT nextval('public.minutes_min_id_seq'::regclass);
 =   ALTER TABLE public.minutes ALTER COLUMN min_id DROP DEFAULT;
       public               postgres    false    229    230    230            %           2604    74223    minutes_subtype sub_id    DEFAULT     �   ALTER TABLE ONLY public.minutes_subtype ALTER COLUMN sub_id SET DEFAULT nextval('public.minutes_subtype_sub_id_seq'::regclass);
 E   ALTER TABLE public.minutes_subtype ALTER COLUMN sub_id DROP DEFAULT;
       public               postgres    false    227    228    228            $           2604    74216    minutes_type type_id    DEFAULT     |   ALTER TABLE ONLY public.minutes_type ALTER COLUMN type_id SET DEFAULT nextval('public.minutes_type_type_id_seq'::regclass);
 C   ALTER TABLE public.minutes_type ALTER COLUMN type_id DROP DEFAULT;
       public               postgres    false    225    226    226            2           2604    74558    motivation_board motivation_id    DEFAULT     �   ALTER TABLE ONLY public.motivation_board ALTER COLUMN motivation_id SET DEFAULT nextval('public.motivation_board_motivation_id_seq'::regclass);
 M   ALTER TABLE public.motivation_board ALTER COLUMN motivation_id DROP DEFAULT;
       public               postgres    false    238    237    238            -           2604    74508    other_doc other_id    DEFAULT     x   ALTER TABLE ONLY public.other_doc ALTER COLUMN other_id SET DEFAULT nextval('public.other_doc_other_id_seq'::regclass);
 A   ALTER TABLE public.other_doc ALTER COLUMN other_id DROP DEFAULT;
       public               postgres    false    234    233    234                       2604    74033    propose_measure propose_id    DEFAULT     �   ALTER TABLE ONLY public.propose_measure ALTER COLUMN propose_id SET DEFAULT nextval('public.propose_measure_propose_id_seq'::regclass);
 I   ALTER TABLE public.propose_measure ALTER COLUMN propose_id DROP DEFAULT;
       public               postgres    false    221    222    222                       2604    74015    staff staff_id    DEFAULT     p   ALTER TABLE ONLY public.staff ALTER COLUMN staff_id SET DEFAULT nextval('public.staff_staff_id_seq'::regclass);
 =   ALTER TABLE public.staff ALTER COLUMN staff_id DROP DEFAULT;
       public               postgres    false    217    218    218            "           2604    74063    trash_bin trash_id    DEFAULT     x   ALTER TABLE ONLY public.trash_bin ALTER COLUMN trash_id SET DEFAULT nextval('public.trash_bin_trash_id_seq'::regclass);
 A   ALTER TABLE public.trash_bin ALTER COLUMN trash_id DROP DEFAULT;
       public               postgres    false    223    224    224            4           2604    74573 &   user_accomplishments accomplishment_id    DEFAULT     �   ALTER TABLE ONLY public.user_accomplishments ALTER COLUMN accomplishment_id SET DEFAULT nextval('public.user_accomplishments_accomplishment_id_seq'::regclass);
 U   ALTER TABLE public.user_accomplishments ALTER COLUMN accomplishment_id DROP DEFAULT;
       public               postgres    false    240    239    240                      0    74483    communication_doc 
   TABLE DATA           �   COPY public.communication_doc (comm_id, comm_date_rcvd, comm_title, comm_venue, comm_remarks, comm_attachfile, comm_is_liquidate, created_by, updated_by, created_at, updated_at) FROM stdin;
    public               postgres    false    232   Ȭ       �          0    74023    condition_type 
   TABLE DATA           <   COPY public.condition_type (cond_id, cond_name) FROM stdin;
    public               postgres    false    220   خ       
          0    74526    history 
   TABLE DATA           j   COPY public.history (history_id, table_name, row_title, staff_id, action_detail, action_date) FROM stdin;
    public               postgres    false    236   L�                 0    74227    minutes 
   TABLE DATA           �   COPY public.minutes (min_id, min_date, min_link, type_id, sub_id, created_by, updated_by, created_at, updated_at, min_series_yr, min_num) FROM stdin;
    public               postgres    false    230   ��                 0    74220    minutes_subtype 
   TABLE DATA           ;   COPY public.minutes_subtype (sub_id, sub_name) FROM stdin;
    public               postgres    false    228   ��                  0    74213    minutes_type 
   TABLE DATA           :   COPY public.minutes_type (type_id, type_name) FROM stdin;
    public               postgres    false    226   �                 0    74555    motivation_board 
   TABLE DATA           l   COPY public.motivation_board (motivation_id, motivation_text, last_updated_by, last_updated_at) FROM stdin;
    public               postgres    false    238   \�                 0    74505 	   other_doc 
   TABLE DATA           �   COPY public.other_doc (other_id, other_date, other_title, other_from, other_status, other_attachfile, created_by, updated_by, created_at, updated_at) FROM stdin;
    public               postgres    false    234   y�       �          0    74030    propose_measure 
   TABLE DATA           l  COPY public.propose_measure (propose_id, propose_date_rcvd, propose_title, propose_rcvd_from, remarks, propose_attachfile, propose_reso_number, propose_ordi_number, propose_session_date, propose_author, propose_is_scan, propose_is_furnish, propose_is_publication, propose_is_posting, cond_id, created_by, updated_by, created_at, updated_at, series_yr) FROM stdin;
    public               postgres    false    222   ��       �          0    74012    staff 
   TABLE DATA           �   COPY public.staff (staff_id, staff_firstname, staff_lastname, staff_prof_pic, staff_birthdate, staff_address, staff_username, staff_password) FROM stdin;
    public               postgres    false    218   ��       �          0    74060 	   trash_bin 
   TABLE DATA           j   COPY public.trash_bin (trash_id, table_name, record_id, deleted_data, deleted_at, deleted_by) FROM stdin;
    public               postgres    false    224   ��                 0    74570    user_accomplishments 
   TABLE DATA           z   COPY public.user_accomplishments (accomplishment_id, staff_id, accomplishment_text, is_completed, created_at) FROM stdin;
    public               postgres    false    240    �       !           0    0    communication_doc_comm_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.communication_doc_comm_id_seq', 22, true);
          public               postgres    false    231            "           0    0    condition_type_cond_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.condition_type_cond_id_seq', 8, true);
          public               postgres    false    219            #           0    0    history_history_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.history_history_id_seq', 250, true);
          public               postgres    false    235            $           0    0    minutes_min_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.minutes_min_id_seq', 29, true);
          public               postgres    false    229            %           0    0    minutes_subtype_sub_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.minutes_subtype_sub_id_seq', 3, true);
          public               postgres    false    227            &           0    0    minutes_type_type_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.minutes_type_type_id_seq', 3, true);
          public               postgres    false    225            '           0    0 "   motivation_board_motivation_id_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public.motivation_board_motivation_id_seq', 10, true);
          public               postgres    false    237            (           0    0    other_doc_other_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.other_doc_other_id_seq', 11, true);
          public               postgres    false    233            )           0    0    propose_measure_propose_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public.propose_measure_propose_id_seq', 104, true);
          public               postgres    false    221            *           0    0    staff_staff_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.staff_staff_id_seq', 3, true);
          public               postgres    false    217            +           0    0    trash_bin_trash_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.trash_bin_trash_id_seq', 77, true);
          public               postgres    false    223            ,           0    0 *   user_accomplishments_accomplishment_id_seq    SEQUENCE SET     Y   SELECT pg_catalog.setval('public.user_accomplishments_accomplishment_id_seq', 13, true);
          public               postgres    false    239            I           2606    74493 (   communication_doc communication_doc_pkey 
   CONSTRAINT     k   ALTER TABLE ONLY public.communication_doc
    ADD CONSTRAINT communication_doc_pkey PRIMARY KEY (comm_id);
 R   ALTER TABLE ONLY public.communication_doc DROP CONSTRAINT communication_doc_pkey;
       public                 postgres    false    232            <           2606    74028 "   condition_type condition_type_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY public.condition_type
    ADD CONSTRAINT condition_type_pkey PRIMARY KEY (cond_id);
 L   ALTER TABLE ONLY public.condition_type DROP CONSTRAINT condition_type_pkey;
       public                 postgres    false    220            M           2606    74534    history history_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.history
    ADD CONSTRAINT history_pkey PRIMARY KEY (history_id);
 >   ALTER TABLE ONLY public.history DROP CONSTRAINT history_pkey;
       public                 postgres    false    236            G           2606    74236    minutes minutes_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.minutes
    ADD CONSTRAINT minutes_pkey PRIMARY KEY (min_id);
 >   ALTER TABLE ONLY public.minutes DROP CONSTRAINT minutes_pkey;
       public                 postgres    false    230            E           2606    74225 $   minutes_subtype minutes_subtype_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.minutes_subtype
    ADD CONSTRAINT minutes_subtype_pkey PRIMARY KEY (sub_id);
 N   ALTER TABLE ONLY public.minutes_subtype DROP CONSTRAINT minutes_subtype_pkey;
       public                 postgres    false    228            C           2606    74218    minutes_type minutes_type_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY public.minutes_type
    ADD CONSTRAINT minutes_type_pkey PRIMARY KEY (type_id);
 H   ALTER TABLE ONLY public.minutes_type DROP CONSTRAINT minutes_type_pkey;
       public                 postgres    false    226            O           2606    74563 &   motivation_board motivation_board_pkey 
   CONSTRAINT     o   ALTER TABLE ONLY public.motivation_board
    ADD CONSTRAINT motivation_board_pkey PRIMARY KEY (motivation_id);
 P   ALTER TABLE ONLY public.motivation_board DROP CONSTRAINT motivation_board_pkey;
       public                 postgres    false    238            K           2606    74514    other_doc other_doc_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.other_doc
    ADD CONSTRAINT other_doc_pkey PRIMARY KEY (other_id);
 B   ALTER TABLE ONLY public.other_doc DROP CONSTRAINT other_doc_pkey;
       public                 postgres    false    234            >           2606    74043 $   propose_measure propose_measure_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.propose_measure
    ADD CONSTRAINT propose_measure_pkey PRIMARY KEY (propose_id);
 N   ALTER TABLE ONLY public.propose_measure DROP CONSTRAINT propose_measure_pkey;
       public                 postgres    false    222            8           2606    74019    staff staff_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_pkey PRIMARY KEY (staff_id);
 :   ALTER TABLE ONLY public.staff DROP CONSTRAINT staff_pkey;
       public                 postgres    false    218            :           2606    74021    staff staff_staff_username_key 
   CONSTRAINT     c   ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_staff_username_key UNIQUE (staff_username);
 H   ALTER TABLE ONLY public.staff DROP CONSTRAINT staff_staff_username_key;
       public                 postgres    false    218            A           2606    74068    trash_bin trash_bin_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.trash_bin
    ADD CONSTRAINT trash_bin_pkey PRIMARY KEY (trash_id);
 B   ALTER TABLE ONLY public.trash_bin DROP CONSTRAINT trash_bin_pkey;
       public                 postgres    false    224            Q           2606    74579 .   user_accomplishments user_accomplishments_pkey 
   CONSTRAINT     {   ALTER TABLE ONLY public.user_accomplishments
    ADD CONSTRAINT user_accomplishments_pkey PRIMARY KEY (accomplishment_id);
 X   ALTER TABLE ONLY public.user_accomplishments DROP CONSTRAINT user_accomplishments_pkey;
       public                 postgres    false    240            ?           1259    74069    idx_trash_bin_deleted_at    INDEX     T   CREATE INDEX idx_trash_bin_deleted_at ON public.trash_bin USING btree (deleted_at);
 ,   DROP INDEX public.idx_trash_bin_deleted_at;
       public                 postgres    false    224            c           2620    74547 /   communication_doc trg_communication_doc_history    TRIGGER     �   CREATE TRIGGER trg_communication_doc_history AFTER INSERT OR DELETE OR UPDATE ON public.communication_doc FOR EACH ROW EXECUTE FUNCTION public.communication_doc_history();
 H   DROP TRIGGER trg_communication_doc_history ON public.communication_doc;
       public               postgres    false    255    232            e           2620    74586 +   motivation_board trg_log_motivation_changes    TRIGGER     �   CREATE TRIGGER trg_log_motivation_changes AFTER INSERT OR UPDATE ON public.motivation_board FOR EACH ROW EXECUTE FUNCTION public.log_motivation_changes();
 D   DROP TRIGGER trg_log_motivation_changes ON public.motivation_board;
       public               postgres    false    242    238            a           2620    74541 /   propose_measure trg_log_propose_measure_changes    TRIGGER     �   CREATE TRIGGER trg_log_propose_measure_changes AFTER INSERT OR DELETE OR UPDATE ON public.propose_measure FOR EACH ROW EXECUTE FUNCTION public.log_propose_measure_changes();
 H   DROP TRIGGER trg_log_propose_measure_changes ON public.propose_measure;
       public               postgres    false    222    254            b           2620    74543    minutes trg_minutes_history    TRIGGER     �   CREATE TRIGGER trg_minutes_history AFTER INSERT OR DELETE OR UPDATE ON public.minutes FOR EACH ROW EXECUTE FUNCTION public.minutes_history();
 4   DROP TRIGGER trg_minutes_history ON public.minutes;
       public               postgres    false    230    257            d           2620    74545    other_doc trg_other_doc_history    TRIGGER     �   CREATE TRIGGER trg_other_doc_history AFTER INSERT OR DELETE OR UPDATE ON public.other_doc FOR EACH ROW EXECUTE FUNCTION public.other_doc_history();
 8   DROP TRIGGER trg_other_doc_history ON public.other_doc;
       public               postgres    false    256    234            Z           2606    74494 3   communication_doc communication_doc_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.communication_doc
    ADD CONSTRAINT communication_doc_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.staff(staff_id) ON UPDATE CASCADE ON DELETE CASCADE;
 ]   ALTER TABLE ONLY public.communication_doc DROP CONSTRAINT communication_doc_created_by_fkey;
       public               postgres    false    3640    218    232            [           2606    74499 3   communication_doc communication_doc_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.communication_doc
    ADD CONSTRAINT communication_doc_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.staff(staff_id) ON UPDATE CASCADE ON DELETE CASCADE;
 ]   ALTER TABLE ONLY public.communication_doc DROP CONSTRAINT communication_doc_updated_by_fkey;
       public               postgres    false    3640    218    232            ^           2606    74535    history history_staff_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.history
    ADD CONSTRAINT history_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id) ON UPDATE CASCADE ON DELETE SET NULL;
 G   ALTER TABLE ONLY public.history DROP CONSTRAINT history_staff_id_fkey;
       public               postgres    false    3640    218    236            V           2606    74247    minutes minutes_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.minutes
    ADD CONSTRAINT minutes_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.staff(staff_id);
 I   ALTER TABLE ONLY public.minutes DROP CONSTRAINT minutes_created_by_fkey;
       public               postgres    false    230    3640    218            W           2606    74242    minutes minutes_sub_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.minutes
    ADD CONSTRAINT minutes_sub_id_fkey FOREIGN KEY (sub_id) REFERENCES public.minutes_subtype(sub_id) ON UPDATE CASCADE ON DELETE CASCADE;
 E   ALTER TABLE ONLY public.minutes DROP CONSTRAINT minutes_sub_id_fkey;
       public               postgres    false    228    3653    230            X           2606    74237    minutes minutes_type_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.minutes
    ADD CONSTRAINT minutes_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.minutes_type(type_id) ON UPDATE CASCADE ON DELETE CASCADE;
 F   ALTER TABLE ONLY public.minutes DROP CONSTRAINT minutes_type_id_fkey;
       public               postgres    false    3651    230    226            Y           2606    74252    minutes minutes_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.minutes
    ADD CONSTRAINT minutes_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.staff(staff_id);
 I   ALTER TABLE ONLY public.minutes DROP CONSTRAINT minutes_updated_by_fkey;
       public               postgres    false    218    3640    230            _           2606    74564 6   motivation_board motivation_board_last_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.motivation_board
    ADD CONSTRAINT motivation_board_last_updated_by_fkey FOREIGN KEY (last_updated_by) REFERENCES public.staff(staff_id) ON DELETE SET NULL;
 `   ALTER TABLE ONLY public.motivation_board DROP CONSTRAINT motivation_board_last_updated_by_fkey;
       public               postgres    false    238    3640    218            \           2606    74515 #   other_doc other_doc_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.other_doc
    ADD CONSTRAINT other_doc_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.staff(staff_id) ON UPDATE CASCADE ON DELETE CASCADE;
 M   ALTER TABLE ONLY public.other_doc DROP CONSTRAINT other_doc_created_by_fkey;
       public               postgres    false    234    3640    218            ]           2606    74520 #   other_doc other_doc_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.other_doc
    ADD CONSTRAINT other_doc_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.staff(staff_id) ON UPDATE CASCADE ON DELETE CASCADE;
 M   ALTER TABLE ONLY public.other_doc DROP CONSTRAINT other_doc_updated_by_fkey;
       public               postgres    false    3640    234    218            R           2606    74044 ,   propose_measure propose_measure_cond_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.propose_measure
    ADD CONSTRAINT propose_measure_cond_id_fkey FOREIGN KEY (cond_id) REFERENCES public.condition_type(cond_id) ON UPDATE CASCADE ON DELETE CASCADE;
 V   ALTER TABLE ONLY public.propose_measure DROP CONSTRAINT propose_measure_cond_id_fkey;
       public               postgres    false    220    222    3644            S           2606    74049 /   propose_measure propose_measure_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.propose_measure
    ADD CONSTRAINT propose_measure_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.staff(staff_id);
 Y   ALTER TABLE ONLY public.propose_measure DROP CONSTRAINT propose_measure_created_by_fkey;
       public               postgres    false    218    3640    222            T           2606    74054 /   propose_measure propose_measure_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.propose_measure
    ADD CONSTRAINT propose_measure_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.staff(staff_id);
 Y   ALTER TABLE ONLY public.propose_measure DROP CONSTRAINT propose_measure_updated_by_fkey;
       public               postgres    false    3640    222    218            U           2606    74548 #   trash_bin trash_bin_deleted_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.trash_bin
    ADD CONSTRAINT trash_bin_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.staff(staff_id) ON DELETE SET NULL;
 M   ALTER TABLE ONLY public.trash_bin DROP CONSTRAINT trash_bin_deleted_by_fkey;
       public               postgres    false    3640    224    218            `           2606    74580 7   user_accomplishments user_accomplishments_staff_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_accomplishments
    ADD CONSTRAINT user_accomplishments_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id) ON DELETE CASCADE;
 a   ALTER TABLE ONLY public.user_accomplishments DROP CONSTRAINT user_accomplishments_staff_id_fkey;
       public               postgres    false    240    218    3640                  x���Qo�0��ͯ�(�����4��i�%[�Iyq�%�BlfR���!�Xh�I<���s������.J,���h�����5g�P�*�l�r�~��k�n� �T���R	��~5����ɣ�Vɟ`j��8A�ȓ�GSJZK�#�'|!� ǀ���>	�4���)`|h�@��pl���>z_�%��tG�T��v s)�����s������9�������F�Q�{ �@lv�Mg<y�$qvC
X:�^iil�7F/��'o����25H�	�6�M{���W�5-\pw_��d3��,K��h)`�!����B�x��~�^��T;Vܻ0�����񆌐~���&�?B���Ƚ� �F�νG�83�x����M�sA���8��ɓ�Z�C��7,���� #�t��'������+:��ow�#O9%=�6l<��[��K�V�:C瘼�]�Kd�XW��x�6h�ayE)|�kc]ϸ�����;��d�p��I�ސ�]�o��m�      �   d   x�3�t�,*.QJML��K�2�NM��K�s�dd!�&��y
�9)\���I9��
��E )3NǢ�̲�.sNǂ��|ӂӿ$#���+F��� û"O      
      x��]�n�H��v���� g/��/�[w�b'މc��Lv(����H-I9�\�;��{^n��T5eY)���xF�ĦX�UWWU�]�D\\�_���>;>�}�<>x�A�G�Q��~���t��σ�3I�I��8�it�ҳ�0yH�C�J;�t8w9cJy/(��d<������$�y�zA����,=��3�q�����#<�("�0�0��Av�.�]��0��A:�ق��#N�t�qJ���`�\#����� �o��j�09i2J���̂��O�D 
A�'@-��Y����$u.�,�i?q2��MG����(�7T�,*�;Rv�q)J�V��Z}�[�Ju(u�"��V���y
����I���̑6�Q�	�{�ǣ �8Wa���s�\���y�H��N�8/�_��uV���.�\H�D�̴§�0�	�D��m�9��-����٬\ͤ�� ��h��$�o����˴Y(Y��m`�s������2G�e�%�������kaZ:Gq<I��m��8=��ȏ�ē���[���NUk�¡���߁%y�	�x�
LY^��M�$��I<���A��8����W��ԏ��1�~4J��j�%0���N7I'�D��ܱ�f�Q?S�ƥue+FNt�t%,�GNo��_&)���P7��I@L�P%���� �8I�1h�M�� �@�L�����t����Ւ��c�&��ǣ%m*AW(`�l��t��y��!NQ���8�C p�8�}�������Y8L�ƶ����E��'���R��L��1���o���|�-P�Ϝ�~�o7
@�;�-�������B�3H@É����6oW��1h����kI�p����(i`�fe����\�Av)v��e/ң�en�[@8���C�,�
ȪX��?��5ø��K(��*���T���Nq�/�d	N]M=��x���q�f�ےW�,].��$��$!{:��v=!�`���a#9%�N\�Q��j8�N"@3+�<�%<��XXC�ۋ ���& fA]&, /(�!��&�͠>R�
B�!��<a���k��e�),�(�h8�g���0�(��YmWԹ�w��wutĬ1�6d��r�R.4�h�kX��0�̍|܆��=��o��'C����*�{�ٙ?L�a�Ϥ9�E� g8w��XH�[���h��߁��o?.�������ffk\�q�&�K�T2�ӷ�����4�	����/
?��0�����U��+���Ny���&H��z������Ѯ��h6� r��&��'�����X��V���͏���[����������Y4����E���N�Κ���<���	���C����3�#��cQ����U�2fA\Ε20װ���ө����<�[߻�����t������]Ma�S-� ��+t�'�QO��+���ϧ�r���&L�0��0x�I�f���K�u$�Ғ6�Q�n�'�ګ��Q:�� ?�����Yo�b#�x����
�P��kFן�~����X'	���0˭��0uz��J/��.�Ρ�*���\�8���w�~�)O��=�9cԩ:^vΙf�b����R,�O�s�\��~�~pz��mS�-
+��KM�
�3�����;x~}�	Pg�B��a,p��w t8%깊r�G�$yF�Orb��1�t��]�xg�M�A.j<�aK�����u( '���W�l��x�s�"�C�C���Hkp�ւ���e(	�J��"m�ʚ�v�BK�a�2F][T ?�o�|�ʢ�7����#�� ě2~�F����t<���8�� ��p���':�������zz��q�Sr���X�B=W!��U�k!]/f����NRdT�R�*2�NڔaE0�A�`�Q$
_�mMT	�.� g���ĸ���7O�04իB!bd_�t�?��]b��g0ȷ�ͭ�[[Ȩ�V`��eu�����#H��[�T�C[X�v��k��ajG#k��]y+p%��)Ok�[Ŭ�
���9\h�a�zU�
������s����ْi��	�Tݫb3�b��Lk�����P��ALwh{��,���S���auޓ��M7y>�:�^n�|4�]P������dj��CI5!������z�$7}����"�#^ZR�'ь(j{%��~��$E����~5}E^�)+��!�������?�����B�����O���x��K�_���&�:���J��g������d�t��~�@靀�s��b�e�(,�yf_@	�J��(���P�J�rIE��%J
)q�ؾ�0RL3
Q�`�X�K�w"�tnZ/SbA��\��``W��Ɩ�.�{g�����a�2��~���뿝�=�-6(��w���7��X��g�\�q
�ԹR�����(�>9?��`嘣�:;ݾ�qk"V@�7�FP���"��� ��3�>/��3N��ٙ����H������<���\ �	�M����c� >� ���7�m%��ww��p���fX+[ψ�V?�Σ^[R�OO�����}���(�6O���%�'S0 
��h�uZ��q��� ��#��fP7H��;� �C�[���H��0���tH��
�>K��ǆW�$`�Y6���&� ��|���izpv����q� �<�_��/Ҷ��\m$���l�E�qŋ�0�\`5RW�a�.�'�)q��p��%XR�x�q�/�QR�i��|���k�l�/��"������C�Q��Q�(C�3jHr�(��,��8t��Wwq��
���2�~���p��Yf yxAy��f�+�jX�3�[�����#;X���oֹ�D��/8�����"A]�!���b��n���j���#��	�C�󼛰���ұB4�Ŵ���M���&�)���nSq���[tـ��n�-ʁ+1m���:螟�}�p�=�:=����n���=i�1�j;'�ҢŶX���a���4c�98�zw|i���\ym�n%�+���Z��X���M2�	��a\�,<`��K��&�#�f�&��A�]�	�0�2D�M�(s���D`�A 2R�Q�#p'�C�4�ӯΉ���ק�6r��jo�4�|M��`��9Q]_.�Å	%u���)sEK�Q��/|<�8���̮V��&[n���Vm��Ze;�����s���``�2�{*��)����Fax��{��]c���Iؚ���M�ZH��R]���F��c�]�SX�1�����ܼ�C[l����
Dk����qo���c�d�h/�=�=M��H]�z,����p�I�,�=��9$O0���*�\�/r�M'�FA�HEE���~u_z]�c�hIǢBK"7	�Ǉ���H,qj�!��K�^4�!WxABP�<�o���wFVG|�M�e��`^�G��/��ϭ�`�SM��BeJ�:�7N�K�٬z�O!����Fh���u���y�7��Mx�� �e�bƕ�6�c}����d�}�d~�����o��f<�5M��
#t�(Ŝ����b�{o��1�A��Ê��	�&-C*N�-�d�H��?���[V�5�*��u�ɀ� jֵ^��4-��PF+̙�tv8��_��!�w*k��J+�-g�-�(��x	�+*1��jh���2M#��`��͊E s�9������]ܢ+wf.ϸ��T� $�
Q!a�g��=�GE��b���7I�ނv�,x��ؚ��m�QU/��C ��T��tC`� ��u���i��G�I�m���/�b�n��,|��!� �$��䶮ev��Aæ����ܓ�"�g�ri\%��䶮a�J��Kٶ�#�|�8��������$�[u�k��<�ar�	�}��_/Λ�>gǷ֯m��L�[���q��g��d�{%������y�on�ݢ�B)\E�� /�mkmۤܙt��6����3f��ac�(�h����k�&d��C�Ӱ�W��^���ӝ�?c<�V�^�`�q� :  �7�zc?�j�e���׮���u�ڣ��&� z�?_\� Hp������}��uTݪ�qK�J�%w�0
���V�k3��S�!�ī4|D��-�X�غ۲V�*�}P3��hU��E���{���r��h��`�u R������f���I���>\B	�T൒���06�����*5��7�-��sc�-�]1��N@���[׊�8�fYY��G��hQT�g�DG �[�ڶ's7\��_�H>B�
:��ە�(T5��]3�2�]a(�g�w���!��Ry(P]��}B�	z����������~���:�ǤGOU��V�l���*��u�R�y|��/�#�l�^��Yn�o��]���G���G[���^�g�0�w��T��m6�;���ظ�R�`��k0��}��L+t�ZBJ�����U�~n��6C��������J���:�mv�|,@��(�����H-�٦#��Y��c��7����n�h���fF?�J��#��ѵ�{�g�e��Cp r%Qf"d���o([�/I�DK`����}j{�c',Wp I��?�/^�?1��D         :  x���KK1���W\7s�In^K*�n�t�FK[�O�h�_o�H���pY$�ǹ	P� }r}
�KUmw�,WO�K=�l�˩�lV?���j7]W�z����`{�u��,�?f��zX�n�7o�٨�yq��sCG�1�c{��d]�����`bS?�?�A�M�Ob5�7�(&��[cN�P�� ϊ�� =Ίl�2�(HWHӎ�VY�,�H��w[��Ĥ�<��,�HQ�� M���vbE�M�e�S]~�Kl�|��zd�em���Z��^�����8�Ȑ�$�Q�V�).!hg$�2�G�����U�         '   x�3�.HM�L��2�JM/�I,�2���w����� ���          0   x�3�N-.����2�(M��LV�HM,��K�2��/�H-����� �v�            x������ � �         F  x���Ao�0���)�e�v(���F�0)]�l�J��WpR���l�DO����$3��D�N>���{����izgqTJ�(��k}h����:��V���{[T�}��[`�*���,n��Â�SjѺC��9�n�TRB�n���9RRZ�,bq��	�YI�W�$�Y�MIW����h`��N�������T{#�^v���i�n��<|�;��Cp����~xft�Z&E��(�R8{EyDX
���6�>8Ц�;��j`�
��[�������f�Z8B��-���D7�Un;���p����я��[II��$4#�R8�?�*���NH��!��,�#���\������>�hƚ��[�n\��?��V�z��`�2�#V0��y?�BO��t�5��z�]ZT#\p�� ���q�#���H�L{׃%��?yw�Ќ����D�5+	�@�3ԉ��!p�����
�Vjl�e�-7�A��&��f7N�9h�"F2J�bV2gw�4N�$�'s���8�J���B+��h����&�ϐ�	��~����{Ɣ���lg�)S���D)M��(�_�_,      �   �  x����r�6���S��� ���fQV�&j2�ݴ�^ �C�
�N�S^�3���I� e���ʚ�ĶdYKI����v�;��G/`Ϲ�*� ��蝒+�`K4�;N7��DW����VL�jEѴ�`�Y�ED����4�|G��]����֙��T�i�����q�eN{���;u��^�����0s� �Yx:����х�_�7R�e浺���KY+�n�BS&$<� t^J����H4���; p
uq�C�?j �G hF��uŤ@���X��*g��iZ�D�L��/i�����B��X)xnJJ�J�Qj�\pR������(s��O��zt��[��jA��)&Ǟ����0u#/���t�A�z���f#�*��.�!X�x~)_��ȼ�3�&��ͅ�	�A
�p:Ԭ>�-�1-8Qf�W�Tmф)]�	l2�q�^� D�7� �1�٠1�:{}�K
6�*���4��&
����8=jh�^-�D	E� �T?$�L����ֱ��H�ʔ�2OB�o�2R˭��A�%�;O�h觮�ѩ@���q��W��=m���+Q)�QTPccƈ�k�9� M���i�xC�_�N��xS��4~F���z�ȥXBnל��P�P�VtM�ڲ�gB<a	��)���z��T� w8,
�$��i�w�,Xz��K��fc$z�00+���rq��u�=����{
��C�%hN�m�����*/E8b$n�#?zF��J���?[�����u��d^�za�%'#�{^o=]�,8�+���5rS(6��+��h��f��=� 8��=L�I}^&CcK�{ip:�H��J5�Ԑ9��,�����V�s�	{�!E���1�]�h�5�򼓥U'��.u�.u�0]�i�50q/̓�y�(��)����4��Y��B_iV*���޺H�n/q��?>�eZ�4="��*(�K^ȕ�@#
iC��a?S�мXI��	��:'��z�*�~-�����|�`�P��#;,�+W�e��n?fN	`3��@Ѳ.���%M� �5���Z�����l���4���I��� ���hB85�;]]��b�]	�
UҴV�a0资t+뵕q	yiy̑��� S�����Da#ۛ�N��+=chA���Q
����0�Y0)`����j�5���/���j��Ds��/�t��a2i�N�6Vڃ�0,$Iz:�K��7��1˕�׿�-��s޸,<�X��*����ю�H�l�yn�Av��ǡF��W��?an��YT�)�i�yf�'d͸m�� �r 7������?w���io_[�[��~��3B;u��G7���J�ff8�@?�'�NЇ��p�����d2�q�p2�d�(O	�T8	��w#��wis����Y|�N��06'�����f~���-�7b���I��=����d����v�C�i�=2Ş�ݖ�݋����      �   �   x����J�P ���)�؝�����ى�(�]����v���E�[����s2�!$!_<�{�n��uI�Ά{حA.�+<WSU�:qq�<_�	�ز��ܮ��D����7X�w���}��h�<l��!ڲ���k���6ߟ+����K�t��١�@	��c@h5�!�`֜�@,��콫i�ǧ�{�>��W�����N8)�/-~�|W
x�3,��0���a!%��r7s�e�z}      �   _  x�ݗ�n7���S���-�����n�4�����.�b�%��q�� ���IJR�bY�,�=I;3;�v0�F�^�^jZu�h������Z��bͰ�r��z��`8t��*Fu5W^�!NOav
��%�61�k��0+�8�i�Fk�ӹ�EN�L&�.��ؾ����6����ңa�S�b����&��֜(&n��Q�B
3������'��h���R��������+X�z���#�̤Z�kU��tM���kzG�3�T}�lvti�U�d�M�ɔܐ�k!�!��e�:�m�L϶DvJ�k\�(�jX%l7���ZF��k5��59��pU>��rV"��|���G%�#X ���~=��&�迁�Ni�Ғpp�c��s�.z��q���Kj�BX����j�Qa�%wȶR��7�>&�?Q�ͬ&����7���;�gQ�	��hPx@@a�Q��4O� >�=wO4@�>�+�;�g�P�F��K��I�&����߸�����)���[0��w��GD8d��/ۖ��� ';Np��ey���x�|t(��2MK4�\}�> 磝 o�{"�g�����;q�JNEM�'��|N:���T�z"��w�_X�
N�D�G^�> &tj��l����ȦQ���x��P�,*��qc����;��t�Dd�ǫ���$��>���
jt�7�AP��qzH��(K���q6�e����U��xq/�N�_���
���/�u/hn��Asq9�z��^���~�j�,���q�QR���v�����FR���Vn\�CQ�o�w�o=�Y��s��e_��({���hZ�8��(�º�.:99��k��         �   x�}�Kj�0�t�9@#���t�l��FuƉ���,5���\Ҕ�VB0���#d�_���3��O'l� �H.�Hy6�n�Q5�4��ZqU*�"��C�G�R!�k��m�p�G�c��c8E?���FK����R!V�����xǻF��~�Kˤ�5��T�~.sC��.�3�U��r?/�!B��9AD�6���E��̑��S�����i��1
�F9��#"]���*��3�����q�     