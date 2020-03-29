# Copyright © 2020 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from decimal import Decimal
from functools import reduce

from flask import Flask
import flask.json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import desc

from search_api.constants import STATE_TYP_CD_ACT, STATE_TYP_CD_HIS


class MyJSONEncoder(flask.json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert decimal instances to strings.
            return str(obj)
        return super(MyJSONEncoder, self).default(obj)


flask.json_encoder = MyJSONEncoder

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DB_CONNECTION_URL', 'postgresql://postgres:password@db/postgres')
# https://stackoverflow.com/questions/33738467/how-do-i-know-if-i-can-disable-sqlalchemy-track-modifications/33790196#33790196
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class BaseModel(db.Model):
    __abstract__ = True

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = getattr(self, c.name)
            if type(d[c.name]) is Decimal:
                d[c.name] = int(d[c.name])
        return d


class Address(BaseModel):
    __tablename__ = "address"
    """
    addr_id                   NUMBER      22     20233825
    province                  CHAR        2      18872463
    country_typ_cd            CHAR        2      19016927
    postal_cd                 VARCHAR2    15     18825296
    addr_line_1               VARCHAR2    50     16862093
    addr_line_2               VARCHAR2    50     3609613
    addr_line_3               VARCHAR2    50     482762
    city                      VARCHAR2    40     17557057
    address_format_type       VARCHAR2    10     3632701
    address_desc              VARCHAR2    300    3372387
    address_desc_short        VARCHAR2    300    3350206
    delivery_instructions     VARCHAR2    80     34510
    unit_no                   VARCHAR2    6      699964
    unit_type                 VARCHAR2    10     11488
    civic_no                  VARCHAR2    6      2210964
    civic_no_suffix           VARCHAR2    10     15768
    street_name               VARCHAR2    30     2221177
    street_type               VARCHAR2    10     2167805
    street_direction          VARCHAR2    10     292073
    lock_box_no               VARCHAR2    5      115988
    installation_type         VARCHAR2    10     47289
    installation_name         VARCHAR2    30     47036
    installation_qualifier    VARCHAR2    15     69
    route_service_type        VARCHAR2    10     146477
    route_service_no          VARCHAR2    4      27530
    province_state_name       VARCHAR2    30     362
    """

    addr_id = db.Column(db.Integer, primary_key=True)
    province = db.Column(db.String(2))
    country_typ_cd = db.Column(db.String(2))
    postal_cd = db.Column(db.String(15))
    addr_line_1 = db.Column(db.String(50))
    addr_line_2 = db.Column(db.String(50))
    addr_line_3 = db.Column(db.String(50))
    city = db.Column(db.String(40))
    address_format_type = db.Column(db.String(10))
    address_desc = db.Column(db.String(300))
    address_desc_short = db.Column(db.String(300))
    delivery_instructions = db.Column(db.String(80))
    unit_no = db.Column(db.String(6))
    unit_type = db.Column(db.String(10))
    civic_no = db.Column(db.String(6))
    civic_no_suffix = db.Column(db.String(10))
    street_name = db.Column(db.String(30))
    street_type = db.Column(db.String(10))
    street_direction = db.Column(db.String(10))
    lock_box_no = db.Column(db.String(5))
    installation_type = db.Column(db.String(10))
    installation_name = db.Column(db.String(30))
    installation_qualifier = db.Column(db.String(15))
    route_service_type = db.Column(db.String(10))
    route_service_no = db.Column(db.String(4))
    province_state_name = db.Column(db.String(30))

    @staticmethod
    def get_address_by_id(id):
        return Address.query.filter(Address.addr_id == id).add_columns(
            Address.addr_line_1,
            Address.addr_line_2,
            Address.addr_line_3,
            Address.postal_cd,
            Address.city,
            Address.province,
            Address.country_typ_cd,
        ).one()[0]


class CorpOpState(BaseModel):
    # A lookup table of states a corporation can be in.
    __tablename__ = 'corp_op_state'
    """
    state_typ_cd       CHAR        3     31
    op_state_typ_cd    CHAR        3     31
    short_desc         VARCHAR2    15    31
    full_desc          VARCHAR2    40    31
    """

    state_typ_cd = db.Column(db.String(3), primary_key=True)
    op_state_typ_cd = db.Column(db.String(3))
    short_desc = db.Column(db.String(15))
    full_desc = db.Column(db.String(40))


class CorpState(BaseModel):
    __tablename__ = 'corp_state'
    """
    corp_num          VARCHAR2    10    4137221
    start_event_id    NUMBER      22    4137221
    end_event_id      NUMBER      22    1930459
    state_typ_cd      CHAR        3     4137221
    dd_corp_num       VARCHAR2    10    11443
    """

    corp_num = db.Column(db.String(10), primary_key=True)
    start_event_id = db.Column(db.Integer)
    end_event_id = db.Column(db.Integer)
    state_typ_cd = db.Column(db.String(3))
    dd_corp_num = db.Column(db.String(10))

    @staticmethod
    def get_corp_states_by_corp_id(id):
        return CorpState.query.filter(
            CorpState.corp_num == id,
            CorpState.end_event_id == None).all()  # noqa: E711


class Corporation(BaseModel):
    __tablename__ = 'corporation'
    """
    corp_num                       VARCHAR2    10     2206759
    corp_frozen_typ_cd             CHAR        1      819
    corp_typ_cd                    VARCHAR2    3      2206759
    recognition_dts                DATE        7      2111082
    last_ar_filed_dt               DATE        7      1025542
    transition_dt                  DATE        7      240802
    bn_9                           VARCHAR2    9      1179842
    bn_15                          VARCHAR2    15     1179165
    accession_num                  VARCHAR2    10     941
    CORP_PASSWORD                  VARCHAR2    300    795500
    PROMPT_QUESTION                VARCHAR2    100    573423
    admin_email                    VARCHAR2    254    703636
    send_ar_ind                    VARCHAR2    1      1642638
    tilma_involved_ind             VARCHAR2    1      2196814
    tilma_cessation_dt             DATE        7      4050
    firm_last_image_date           DATE        7      51550
    os_session                     NUMBER      22     420543
    last_agm_date                  DATE        7      48416
    firm_lp_xp_termination_date    DATE        7      7443
    last_ledger_dt                 DATE        7      1
    ar_reminder_option             VARCHAR2    10     69086
    ar_reminder_date               VARCHAR2    20     67640
    TEMP_PASSWORD                  VARCHAR2    300    3582
    TEMP_PASSWORD_EXPIRY_DATE      DATE        7      3582
    """

    corp_num = db.Column(db.String(10), primary_key=True, unique=True)
    corp_frozen_typ_cd = db.Column(db.String(1))
    corp_typ_cd = db.Column(db.String(3))
    recognition_dts = db.Column(db.Date)
    last_ar_filed_dt = db.Column(db.Date)
    transition_dt = db.Column(db.Date)
    bn_9 = db.Column(db.String(9))
    bn_15 = db.Column(db.String(15))
    accession_num = db.Column(db.String(10))
    admin_email = db.Column(db.String(254))
    send_ar_ind = db.Column(db.String(1))
    tilma_involved_ind = db.Column(db.String(1))
    tilma_cessation_dt = db.Column(db.Date)
    firm_last_image_date = db.Column(db.Date)
    os_session = db.Column(db.Integer)
    last_agm_date = db.Column(db.Date)
    firm_lp_xp_termination_date = db.Column(db.Date)
    last_ledger_dt = db.Column(db.Date)
    ar_reminder_option = db.Column(db.String(10))
    ar_reminder_date = db.Column(db.String(20))

    def __repr__(self):
        return 'corp num: {}'.format(self.corp_num)

    @staticmethod
    def get_corporation_by_id(id):
        return (
            Corporation.query
            .add_columns(
                Corporation.corp_num,
                Corporation.transition_dt,
                Corporation.admin_email,
            )
            .filter(Corporation.corp_num == id).one())[0]

    @staticmethod
    def query_corporations(query, sort_type, sort_value):
        results = (
            Corporation.query
            .join(CorpName, Corporation.corp_num == CorpName.corp_num)
            .join(CorpParty, Corporation.corp_num == CorpParty.corp_num)
            .join(Office, Office.corp_num == Corporation.corp_num)
            .join(CorpState, CorpState.corp_num == CorpParty.corp_num)
            .join(CorpOpState, CorpOpState.state_typ_cd == CorpState.state_typ_cd)
            .join(Address, Office.mailing_addr_id == Address.addr_id)
            .with_entities(
                CorpName.corp_nme,
                Corporation.corp_num,
                Corporation.corp_typ_cd,
                Corporation.recognition_dts,
                CorpOpState.state_typ_cd,
                Address.addr_line_1,
                Address.addr_line_2,
                Address.addr_line_3,
                Address.postal_cd,
            )
        )

        results = results.filter(
            (Corporation.corp_num == query) |
            (CorpName.corp_nme.ilike('%' + query + '%'))
        )

        # Sorting
        if sort_type is None:
            results = results.order_by(Corporation.corp_nme)
        else:
            field = _get_sort_field(sort_value)

            if sort_type == 'dsc':
                results = results.order_by(field.desc())
            else:
                results = results.order_by(field)


class CorpName(BaseModel):
    __tablename__ = 'corp_name'
    """
    corp_num             VARCHAR2    10     2484908
    corp_name_typ_cd     CHAR        2      2484908
    start_event_id       NUMBER      22     2484908
    corp_name_seq_num    NUMBER      22     2484908
    end_event_id         NUMBER      22     251437
    srch_nme             VARCHAR2    35     2484908
    corp_nme             VARCHAR2    150    2484909
    dd_corp_num          VARCHAR2    10     11929
    """

    corp_num = db.Column(db.String(10), primary_key=True)
    corp_name_seq_num = db.Column(db.Integer)
    corp_name_typ_cd = db.Column(db.String(2))
    start_event_id = db.Column(db.Integer)
    end_event_id = db.Column(db.Integer)
    srch_nme = db.Column(db.String(35))
    corp_nme = db.Column(db.String(150))
    dd_corp_num = db.Column(db.String(10))

    def __repr__(self):
        return 'corp num: {}'.format(self.corp_num)

    @staticmethod
    def get_corp_name_by_corp_id(id):
        return CorpName.query.filter_by(corp_num=id).order_by(desc(CorpName.end_event_id))


class Office(BaseModel):
    __tablename__ = "office"
    """
    corp_num            VARCHAR2    10    4544141
    office_typ_cd       CHAR        2     4544141
    start_event_id      NUMBER      22    4544141
    end_event_id        NUMBER      22    1578071
    mailing_addr_id     NUMBER      22    4533953
    delivery_addr_id    NUMBER      22    4527193
    dd_corp_num         VARCHAR2    10    23155
    email_address       VARCHAR2    75    14906
    """

    corp_num = db.Column(db.String(10), primary_key=True)
    office_typ_cd = db.Column(db.String(2), primary_key=True)
    start_event_id = db.Column(db.Integer, primary_key=True)
    end_event_id = db.Column(db.Integer)
    mailing_addr_id = db.Column(db.Integer)
    delivery_addr_id = db.Column(db.Integer)
    dd_corp_num = db.Column(db.String(10))
    email_address = db.Column(db.String(75))

    @staticmethod
    def get_offices_by_corp_id(id):
        return Office.query.filter_by(corp_num=id, end_event_id=None)


class OfficeType(BaseModel):
    __tablename__ = "office_type"
    """
    office_typ_cd    CHAR        2     9
    short_desc       VARCHAR2    15    9
    full_desc        VARCHAR2    40    9
    """

    office_typ_cd = db.Column(db.String(2), primary_key=True)
    short_desc = db.Column(db.String(15))
    full_desc = db.Column(db.String(40))


class CorpParty(BaseModel):
    __tablename__ = 'corp_party'

    """
    corp_party_id             NUMBER      22     11748880
    mailing_addr_id           NUMBER      22     8369745
    delivery_addr_id          NUMBER      22     7636885
    corp_num                  VARCHAR2    10     11748884
    party_typ_cd              CHAR        3      11748884
    start_event_id            NUMBER      22     11748884
    end_event_id              NUMBER      22     6194691
    prev_party_id             NUMBER      22     3623071
    corr_typ_cd               CHAR        1      230615
    last_report_dt            DATE        7      50
    appointment_dt            DATE        7      3394297
    cessation_dt              DATE        7      3071988
    last_nme                  VARCHAR2    30     11397162
    middle_nme                VARCHAR2    30     2773092
    first_nme                 VARCHAR2    30     11392744
    business_nme              VARCHAR2    150    369824
    bus_company_num           VARCHAR2    15     108582
    email_address             VARCHAR2    254    10442
    corp_party_seq_num        NUMBER      22     27133
    OFFICE_NOTIFICATION_DT    DATE        7      8380
    phone                     VARCHAR2    30     4306
    reason_typ_cd             VARCHAR2    3      0
    """
    corp_party_id = db.Column(db.Integer, primary_key=True)
    mailing_addr_id = db.Column(db.Integer)
    delivery_addr_id = db.Column(db.Integer)
    corp_num = db.Column(db.String(10))
    party_typ_cd = db.Column(db.String(3))
    start_event_id = db.Column(db.Integer)
    end_event_id = db.Column(db.Integer)
    prev_party_id = db.Column(db.Integer)
    corr_typ_cd = db.Column(db.String(1))
    last_report_dt = db.Column(db.Date)
    appointment_dt = db.Column(db.Date)
    cessation_dt = db.Column(db.Date)
    last_nme = db.Column(db.String(30))
    middle_nme = db.Column(db.String(30))
    first_nme = db.Column(db.String(30))
    business_nme = db.Column(db.String(150))
    bus_company_num = db.Column(db.String(15))
    email_address = db.Column(db.String(254))
    corp_party_seq_num = db.Column(db.Integer)
    phone = db.Column(db.String(30))
    reason_typ_cd = db.Column(db.String(3))

    def __repr__(self):
        return 'corp num: {}'.format(self.corp_party_id)

    @staticmethod
    def get_corp_party_by_id(id):
        return CorpParty.query.filter(CorpParty.corp_party_id == int(id)).one()

    @staticmethod
    def get_corporation_info_by_corp_party_id(id):
        return (
            CorpParty.query.filter(CorpParty.corp_party_id == int(id))
            .join(Corporation, Corporation.corp_num == CorpParty.corp_num)
            .add_columns(
                Corporation.corp_typ_cd,
                Corporation.admin_email
            ).one())

    @staticmethod
    def get_filing_description_by_corp_party_id(id):
        return (
            CorpParty.query
            .join(Event, Event.event_id == CorpParty.start_event_id)
            .join(Filing, Filing.event_id == Event.event_id)
            .join(FilingType, FilingType.filing_typ_cd == Filing.filing_typ_cd)
            .add_columns(FilingType.full_desc)
            .filter(CorpParty.corp_party_id == int(id)).all())

    @staticmethod
    def get_offices_held_by_corp_party_id(id):
        return (
            CorpParty.query
            .join(OfficesHeld, OfficesHeld.corp_party_id == CorpParty.corp_party_id)
            .join(OfficerType, OfficerType.officer_typ_cd == OfficesHeld.officer_typ_cd)
            .join(Event, Event.event_id == CorpParty.start_event_id)
            .add_columns(
                CorpParty.corp_party_id,
                OfficerType.officer_typ_cd,
                OfficerType.short_desc,
                CorpParty.appointment_dt,
                Event.event_timestmp
            )
            .filter(CorpParty.corp_party_id == int(id))
        )

    @staticmethod
    def get_corp_party_at_same_addr(id):
        person = CorpParty.get_corp_party_by_id(id)

        # one or both addr may be null, handle each case.
        if person.delivery_addr_id or person.mailing_addr_id:
            if person.delivery_addr_id and person.mailing_addr_id:
                expr = (CorpParty.delivery_addr_id == person.delivery_addr_id) | \
                    (CorpParty.mailing_addr_id == person.mailing_addr_id)
            elif person.delivery_addr_id:
                expr = (CorpParty.delivery_addr_id == person.delivery_addr_id)
            elif person.mailing_addr_id:
                expr = (CorpParty.mailing_addr_id == person.mailing_addr_id)

            same_addr = (
                CorpParty.query
                .join(Event, Event.event_id == CorpParty.start_event_id)
                .add_columns(Event.event_timestmp)
                .filter(expr)
            )
        else:
            same_addr = []

        return same_addr

    @staticmethod
    def get_corp_party_same_name_at_same_addr(id):
        person = CorpParty.get_corp_party_by_id(id)
        same_name_and_company = (
            CorpParty.query
            .join(Event, Event.event_id == CorpParty.start_event_id)
            .add_columns(Event.event_timestmp)
        )

        if person.first_nme:
            same_name_and_company = same_name_and_company.filter(
                CorpParty.first_nme.ilike(person.first_nme))

        if person.last_nme:
            same_name_and_company = same_name_and_company.filter(
                CorpParty.last_nme.ilike(person.last_nme))

        if person.corp_num:
            same_name_and_company = same_name_and_company.filter(
                CorpParty.corp_num.ilike(person.corp_num))

        return same_name_and_company

    @staticmethod
    def query_corp_parties(clauses, mode, sort_type, sort_value):
        results = (
            CorpParty.query
            .join(Corporation, Corporation.corp_num == CorpParty.corp_num)
            .join(CorpState, CorpState.corp_num == CorpParty.corp_num)
            .join(CorpOpState, CorpOpState.state_typ_cd == CorpState.state_typ_cd)
            .join(CorpName, Corporation.corp_num == CorpName.corp_num)
            .join(Address, CorpParty.mailing_addr_id == Address.addr_id)
            .add_columns(
                CorpParty.corp_party_id,
                CorpParty.first_nme,
                CorpParty.middle_nme,
                CorpParty.last_nme,
                CorpParty.appointment_dt,
                CorpParty.cessation_dt,
                CorpParty.corp_num,
                CorpParty.party_typ_cd,
                CorpName.corp_nme,
                Address.addr_line_1,
                Address.addr_line_2,
                Address.addr_line_3,
                Address.postal_cd,
                CorpOpState.state_typ_cd,
            ))

        # Determine if we will combine clauses with OR or AND. mode=ALL means we use AND. Default mode is OR
        if mode == 'ALL':
            def fn(accumulator, s):
                return accumulator & _get_filter(*s)
        else:
            def fn(accumulator, s):
                return accumulator | _get_filter(*s)

        # We use reduce here to join all the items in clauses with the & operator or the | operator.
        # Similar to if we did "|".join(clause), but calling the boolean operator instead.
        filter_grp = reduce(
            fn,
            clauses[1:],
            _get_filter(*clauses[0])
        )
        results = results.filter(filter_grp)

        # Sorting
        if sort_type is None:
            results = results.order_by(CorpParty.last_nme, CorpParty.corp_num)
        else:
            field = _get_sort_field(sort_value)

            if sort_type == 'dsc':
                results = results.order_by(field.desc())
            else:
                results = results.order_by(field)

        return results


class Event(BaseModel):
    __tablename__ = "event"
    """
    EVENT_ID          NUMBER      22    17616460
    CORP_NUM          VARCHAR2    10    17616460
    EVENT_TYP_CD      VARCHAR2    10    17616460
    EVENT_TIMESTMP    DATE        7     17616461
    TRIGGER_DTS       DATE        7     1126833
    """

    event_id = db.Column(db.Integer, unique=True, primary_key=True)
    corp_num = db.Column(db.String(10))
    event_type_cd = db.Column(db.String(10))
    event_timestmp = db.Column(db.Date)
    trigger_dts = db.Column(db.Date)


class OfficerType(BaseModel):
    __tablename__ = "officer_type"
    """
    officer_typ_cd    CHAR        3      9
    short_desc        VARCHAR2    75     9
    full_desc         VARCHAR2    125    9
    """

    officer_typ_cd = db.Column(db.String(3), primary_key=True)
    short_desc = db.Column(db.String(75))
    full_desc = db.Column(db.String(125))


class OfficesHeld(BaseModel):
    __tablename__ = "offices_held"
    """
    corp_party_id       NUMBER    22    3694791
    officer_typ_cd      CHAR      3     3694794
    dd_corp_party_id    NUMBER    22    7
    """

    corp_party_id = db.Column(db.Integer, primary_key=True)
    officer_typ_cd = db.Column(db.String(3), primary_key=True)
    dd_corp_party_id = db.Column(db.Integer)


class Filing(BaseModel):
    __tablename__ = "filing"
    """
    EVENT_ID            NUMBER      22      13775802
    FILING_TYP_CD       CHAR        5       13775803
    EFFECTIVE_DT        DATE        7       13775801
    CHANGE_DT           DATE        7       386466
    REGISTRATION_DT     DATE        7       0
    PERIOD_END_DT       DATE        7       5529986
    ACCESSION_NUM       CHAR        10      0
    ARRANGEMENT_IND     CHAR        1       8212197
    AUTH_SIGN_DT        DATE        7       8276
    WITHDRAWN_EVENT_ID  NUMBER      22      325
    ODS_TYP_CD          CHAR        2       13119449
    DD_EVENT_ID         NUMBER      22      670145
    ACCESS_CD           VARCHAR2    9       4664766
    NR_NUM              VARCHAR2    10      968307
    COURT_APPR_IND      CHAR        1       15787
    COURT_ORDER_NUM     VARCHAR2    255     2069
    AGM_DATE            DATE        7       582818
    NEW_CORP_NUM        VARCHAR2    10      5
    """

    event_id = db.Column(db.Integer, primary_key=True)
    filing_typ_cd = db.Column(db.String(5))
    effective_dt = db.Column(db.Date)
    change_dt = db.Column(db.Date)
    registration_dt = db.Column(db.Date)
    period_end_dt = db.Column(db.Date)
    accession_num = db.Column(db.String(10))
    arrangement_ind = db.Column(db.String(1))
    auth_sign_dt = db.Column(db.Date)
    withdrawn_event_id = db.Column(db.Integer)
    ods_typ_cd = db.Column(db.String(2))
    dd_event_id = db.Column(db.Integer)
    access_cd = db.Column(db.String(9))
    nr_num = db.Column(db.String(10))
    court_appr_ind = db.Column(db.String(1))
    court_order_num = db.Column(db.String(255))
    agm_date = db.Column(db.Date)
    new_corp_num = db.Column(db.String(10))


class FilingType(BaseModel):
    __tablename__ = "filing_type"
    """
    FILING_TYP_CD       CHAR        5      420
    FILING_TYP_CLASS    VARCHAR2    10     420
    SHORT_DESC          VARCHAR2    50     420
    FULL_DESC           VARCHAR2    125    420
    """

    filing_typ_cd = db.Column(db.String(5), primary_key=True)
    filing_typ_class = db.Column(db.String(10))
    short_desc = db.Column(db.String(50))
    full_desc = db.Column(db.String(125))


def _merge_corpparty_search_addr_fields(row):
    address = row.addr_line_1
    if row.addr_line_2:
        address += ", " + row.addr_line_2
    if row.addr_line_3:
        address += ", " + row.addr_line_3
    return address


def _is_addr_search(fields):
    return "addr_line_1" in fields or "postal_cd" in fields


def _get_model_by_field(field_name):
    if field_name in ['first_nme', 'middle_nme', 'last_nme', 'appointment_dt', 'cessation_dt', 'corp_num',
                      'corp_party_id', 'party_typ_cd']:  # CorpParty fields
        return eval('CorpParty')
    elif field_name in ['corp_num', 'recognition_dts', 'corp_typ_cd']:  # Corporation fields
        return eval('Corporation')
    elif field_name in ['corp_nme']:  # CorpName fields
        return eval('CorpName')
    elif field_name in ['addr_line_1', 'addr_line_2', 'addr_line_3', 'postal_cd', 'city', 'province']:  # Address fields
        return eval('Address')
    elif field_name in ['state_typ_cd']:
        return eval('CorpOpState')


def _get_filter(field, operator, value):

    if field == 'any_nme':
        return (
            _get_filter('first_nme', operator, value) |
            _get_filter('middle_nme', operator, value) |
            _get_filter('last_nme', operator, value))

    if field == 'addr':
        return (
            _get_filter('addr_line_1', operator, value) |
            _get_filter('addr_line_2', operator, value) |
            _get_filter('addr_line_3', operator, value))

    if field == 'state_typ_cd':
        # state_typ_cd is either "ACT", or displayed as "HIS" for any other value
        if value == STATE_TYP_CD_ACT:
            operator = 'exact'
        elif value == STATE_TYP_CD_HIS:
            operator = 'excludes'
            value = STATE_TYP_CD_ACT

    model = _get_model_by_field(field)

    value = value.lower()
    if model:
        Field = getattr(model, field)
        # TODO: we should sanitize the values
        if operator == 'contains':
            return Field.ilike('%' + value + '%')
        elif operator == 'exact':
            return Field.ilike(value)
        elif operator == 'endswith':
            return Field.ilike('%' + value)
        elif operator == 'startswith':
            return Field.ilike(value + '%')
        elif operator == 'wildcard':
            # We support entering * or % as wildcards, but the actual wildcard is %
            value = value.replace("*", "%")
            return Field.ilike(value)
        elif operator == 'excludes':
            return ~Field.ilike(value)
        else:
            raise Exception('invalid operator: {}'.format(operator))
    else:
        raise Exception('invalid field: {}'.format(field))


def _get_sort_field(field_name):

    model = _get_model_by_field(field_name)
    if model:
        return getattr(model, field_name)
    else:
        raise Exception('invalid sort field: {}'.format(field_name))


def _get_corporation_search_results(args):
    query = args.get("query")

    sort_type = args.get('sort_type')
    sort_value = args.get('sort_value')

    if not query:
        return "No search query was received", 400

<<<<<<< HEAD
    # TODO: move queries to model class.
    results = (
        Corporation.query
        .join(CorpName, Corporation.corp_num == CorpName.corp_num)
        .join(CorpParty, Corporation.corp_num == CorpParty.corp_num)
        .join(Office, Office.corp_num == Corporation.corp_num)
        .join(CorpState, CorpState.corp_num == CorpParty.corp_num)
        .join(CorpOpState, CorpOpState.state_typ_cd == CorpState.state_typ_cd)
        .join(Address, Office.mailing_addr_id == Address.addr_id)
        .with_entities(
            CorpName.corp_nme,
            Corporation.corp_num,
            Corporation.corp_typ_cd,
            Corporation.recognition_dts,
            CorpOpState.state_typ_cd,
            Address.addr_line_1,
            Address.addr_line_2,
            Address.addr_line_3,
            Address.postal_cd,
        )
        .filter(CorpName.end_event_id == None)
        # .filter(Office.end_event_id == None)
    )

    results = results.filter(
        (Corporation.corp_num == query) |
        (CorpName.corp_nme.ilike('%' + query + '%'))
    )

    results = Corporation.query_corporations(query, sort_type, sort_value)
    return results


def _get_corpparty_search_results(args):
    """
    Querystring parameters as follows:

    You may provide any number of querystring triples such as

    field=ANY_NME|first_nme|last_nme|<any column name>
    &operator=exact|contains|startswith|endswith
    &value=<string>
    &sort_type=asc|desc
    &sort_value=ANY_NME|first_nme|last_nme|<any column name>

    For example, to get everyone who has any name that starts with 'Sky', or last name must be exactly 'Little', do:
    curl "http://localhost/api/v1/directors/search/?field=ANY_NME&operator=startswith&value=Sky&field=last_nme&operator=exact&value=Little&mode=ALL"  # noqa
    """

    query = args.get("query")

    fields = args.getlist('field')
    operators = args.getlist('operator')
    values = args.getlist('value')
    mode = args.get('mode')
    sort_type = args.get('sort_type')
    sort_value = args.get('sort_value')

    if query and len(fields) > 0:
        raise Exception("use simple query or advanced. don't mix")

    # Only triples of clauses are allowed. So, the same number of fields, ops and values.
    if len(fields) != len(operators) or len(operators) != len(values):
        raise Exception("mismatched query param lengths: fields:{} operators:{} values:{}".format(
            len(fields),
            len(operators),
            len(values)))

    # Zip the lists, so ('last_nme', 'first_nme') , ('contains', 'exact'), ('Sky', 'Apple') =>
    #  (('last_nme', 'contains', 'Sky'), ('first_nme', 'exact', 'Apple'))
    clauses = list(zip(fields, operators, values))

    results = CorpParty.query_corp_parties(clauses, mode, sort_type, sort_value)

    return results


def _normalize_addr(id):
    if not id:
        return ''

    address = Address.get_address_by_id(id)

    def fn(accumulator, s):
        if s:
            return ((accumulator or '') + ', ' if accumulator else '') + (s or '')
        else:
            return accumulator or ''

    return reduce(fn, [address.addr_line_1, address.addr_line_2, address.addr_line_3,
                       address.city, address.province, address.country_typ_cd])


def _format_office_typ_cd(office_typ_cd):
    if office_typ_cd == "RG":
        return "Registered"
    elif office_typ_cd == "RC":
        return "Records"
