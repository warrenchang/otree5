from os import environ

SESSION_CONFIGS = [
    dict(
        name='DoubleAuction',
        display_name='Double Auction',
        app_sequence=['double_auction'],
        num_demo_participants=6,
    ),
    dict(
        name='GoodsMarket',
        display_name='Pit market',
        app_sequence=['GoodsMarket'],
        num_demo_participants=7,
        market_time=300,
        randomise_types=True,
        short_selling=True,
        margin_buying=True,
    ),
    # dict(
    #     name='sPartitions',
    #     display_name='single asset: Aggregation mechanisms for crowd predictions on partitions',
    #     app_sequence=['singleAssetInfo'],
    #     num_demo_participants=4,
    #     market_time=300,
    #     randomise_types=True,
    #     short_selling=True,
    #     margin_buying=True,
    # ),
    # dict(
    #     name='nPartitions',
    #     display_name='n assets: Aggregation mechanisms for crowd predictions with multiple assets on partitions',
    #     app_sequence=['nAssetsInfo'],
    #     num_demo_participants=4,
    #     market_time=210,
    #     randomise_types=True,
    #     short_selling=True,
    #     margin_buying=True,
    # ),
    dict(
        name='singleAsset',
        display_name='Single asset: Continuous double auction',
        app_sequence=['singleAsset'],
        num_demo_participants=4,
        market_time=210,
        randomise_types=True,
        short_selling=False,
        margin_buying=False,
        ),
    dict(
        name='nAssets',
        display_name='n assets: Continuous double auction',
        app_sequence=['nAssets'],
        num_demo_participants=5,
        market_time=210,
        randomise_types=True,
        short_selling=True,
        margin_buying=True,
        ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['roleID', 'isObserver', 'isParticipating', 'informed']
SESSION_FIELDS = ['numParticipants']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
SECRET_KEY = '776841529'

DEMO_PAGE_INTRO_HTML = """ """

INSTALLED_APPS = ['otree']
#DEBUG = False
#AUTH_LEVEL = DEMO


ROOMS = [
    {
        'name': 'dpn',
        'display_name': 'DPN Class',
        'participant_label_file': '_rooms/dpn.txt',
    },
    {
        'name': 'be',
        'display_name': 'BE Class',
        'participant_label_file': '_rooms/be.txt',
    },
    {
        'name': 'mba',
        'display_name': 'MBA Class',
        'participant_label_file': '_rooms/mba.txt',
    },
    {
        'name': 'sdc',
        'display_name': 'SDC',
        'participant_label_file': '_rooms/sdc.txt',
    },
    {
        'name': '1',
        'display_name': 'Room 1',
        'participant_label_file': '_rooms/1.txt',
    },
    {
        'name': '2',
        'display_name': 'Room 2',
        'participant_label_file': '_rooms/2.txt',
    },
    {
        'name': '3',
        'display_name': 'Room 3',
        'participant_label_file': '_rooms/3.txt',
    },
]