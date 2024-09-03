from otree.api import *
import time
import random


doc = "Double auction market"


class C(BaseConstants):
    NAME_IN_URL = 'double_auction'
    PLAYERS_PER_GROUP = None
    market_time = 300  # needed to initialize variables but exchanged by session_config
    NUM_ROUNDS = 6
    ITEMS_PER_SELLER = [1,3] # number of goods for the two parts of the experiment
    PRODUCTION_COST = cu(0)
    SUNK_COST = cu(10)
    SELLER = 'Seller'  # Role for sellers
    BUYER_25 = 'Buyer_25'  # Role for demander with value 25
    BUYER_20 = 'Buyer_20'  # Role for demander with value 20
    BUYER_5 = 'Buyer_5'  # Role for demander with value 5
    BUYER = 'Buyer'  # Role for demander with value 5

    VALUATION_MIN = cu(5)
    VALUATION_MAX = cu(50)
    # PRODUCTION_COSTS_MIN = cu(10)
    # PRODUCTION_COSTS_MAX = cu(80)


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    # experiment consists of two parts, with different number of items, and buyer values swap between two types of buyers
    players = subsession.get_players()

    if subsession.round_number == 1:
        total_players = len(players)
        n = total_players // 6  # Calculate the number of each role type
        r = total_players % 6

        roles_distribution = {
            C.BUYER_25: n + (1 if r > 0 else 0),
            C.BUYER_20: 2 * n + (1 if r > 1 else 0) + (1 if r > 2 else 0),
            C.BUYER_5: n + (1 if r > 3 else 0),
            C.SELLER: 2 * n + (1 if r > 4 else 0) + (1 if r > 5 else 0),
        }
        role_list = [C.BUYER_25] * roles_distribution[C.BUYER_25] + \
                    [C.BUYER_20] * roles_distribution[C.BUYER_20] + \
                    [C.BUYER_5] * roles_distribution[C.BUYER_5] + \
                    [C.SELLER] * roles_distribution[C.SELLER]
        random.shuffle(role_list)  # Shuffle to randomly assign roles

        # print('round', subsession.round_number, 'num players', total_players)
        for p, role in zip(players, role_list):
            print(p,role)
            if role == C.SELLER:
                p.player_role = role
                p.num_items = C.ITEMS_PER_SELLER[0]
                p.breakeven_point = 0
                # p.current_offer = C.VALUATION_MAX
            else:
                p.player_role = C.BUYER
                # p.current_offer = 0
                p.num_items = 0
                if role == C.BUYER_25:
                    p.breakeven_point = 25
                elif role == C.BUYER_20:
                    p.breakeven_point = 20
                elif role == C.BUYER_5:
                    p.breakeven_point = 5
            p.participant.vars['role'] = p.player_role
            p.participant.vars['breakeven_point'] = p.breakeven_point
            p.participant.vars['num_items'] = p.num_items
            # p.participant.vars['initial_offer'] = p.current_offer
            p.is_buyer = p.player_role == C.BUYER
    elif subsession.round_number == int((C.NUM_ROUNDS+1)/2)+1: ## switching buyer_5 and buyer_25 halfway
        for p in players:
            # print('participant.role', p.participant.vars.get('role', ''))
            p.player_role = p.participant.vars['role']
            if p.player_role == C.BUYER:
                # p.current_offer = 0
                p.num_items = 0
                if p.participant.vars['breakeven_point'] == 25:
                    p.breakeven_point = 5
                elif p.participant.vars['breakeven_point'] == 5:
                    p.breakeven_point = 25
                else:
                    p.breakeven_point = 20
            else:
                p.breakeven_point = 0
                p.num_items = C.ITEMS_PER_SELLER[1]
                # p.current_offer = C.VALUATION_MAX
            p.participant.vars['breakeven_point'] = p.breakeven_point
            p.participant.vars['num_items'] = p.num_items
            # p.participant.vars['initial_offer'] = p.current_offer
            p.is_buyer = p.player_role == C.BUYER
    else:
        for p in players:
            # print('participant.role', p.participant.vars.get('role', ''))
            p.player_role = p.participant.vars['role']
            p.breakeven_point = p.participant.vars['breakeven_point']
            p.num_items = p.participant.vars['num_items']
            # p.current_offer = p.participant.vars['initial_offer']
            p.is_buyer = p.player_role == C.BUYER




class Group(BaseGroup):
    start_timestamp = models.IntegerField()


class Player(BasePlayer):
    is_buyer = models.BooleanField()
    player_role = models.StringField()  # Role of the player (seller, demander_20, demander_25, demander_5)
    current_offer = models.IntegerField(initial=None,min=0)
    breakeven_point = models.CurrencyField()
    num_items = models.IntegerField()


class Transaction(ExtraModel):
    group = models.Link(Group)
    buyer = models.Link(Player)
    seller = models.Link(Player)
    price = models.CurrencyField()
    seconds = models.IntegerField(doc="Timestamp (seconds since beginning of trading)")


def live_method(player: Player, data):
    group = player.group
    players = group.get_players()
    # get the buyers and sellers who have made offers
    buyers = [p for p in players if p.is_buyer and (p.field_maybe_none('current_offer') is not None)]
    sellers = [p for p in players if not p.is_buyer and (p.field_maybe_none('current_offer') is not None)]
    news = None
    if data:
        offer = int(data['offer'])
        player.current_offer = offer
        print(offer, player.current_offer)
        match = []
        if player.is_buyer:
            if player not in buyers:
                buyers.append(player)
            if len(sellers)>0:
                best_offer_seller = min(sellers, key=lambda p: p.current_offer)
                if best_offer_seller.num_items > 0 and best_offer_seller.current_offer <= player.current_offer:
                    match = [player,best_offer_seller]
        else:
            if player not in sellers:
                sellers.append(player)
            if len(buyers)>0:
                best_offer_buyer = max(buyers, key=lambda p: p.current_offer)
                if player.num_items > 0 and player.current_offer <= best_offer_buyer.current_offer:
                    match = [best_offer_buyer,player]
        if match:
            [buyer, seller] = match
            price = (buyer.current_offer+seller.current_offer)/2
            Transaction.create(
                group=group,
                buyer=buyer,
                seller=seller,
                price=price,
                seconds=int(time.time() - group.start_timestamp),
            )
            buyer.num_items += 1
            seller.num_items -= 1
            buyer.payoff += buyer.breakeven_point - price
            seller.payoff += price - seller.breakeven_point
            # buyer.current_offer = 0
            # seller.current_offer = C.VALUATION_MAX
            buyer.current_offer = None
            seller.current_offer = None
            news = dict(buyer=buyer.id_in_group, seller=seller.id_in_group, price=price)

    bids = sorted([p.current_offer for p in buyers if (p.field_maybe_none('current_offer') is not None)], reverse=True)
    asks = sorted([p.current_offer for p in sellers if (p.field_maybe_none('current_offer') is not None)])
    print(bids, asks)
    highcharts_series = [[tx.seconds, tx.price] for tx in Transaction.filter(group=group)]

    return {
        p.id_in_group: dict(
            num_items=p.num_items,
            current_offer=p.field_maybe_none('current_offer'),
            payoff=p.payoff,
            bids=bids,
            asks=asks,
            highcharts_series=highcharts_series,
            news=news,
        )
        for p in players
    }


# PAGES
class WaitToStart(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.start_timestamp = int(time.time())


class Trading(Page):
    live_method = live_method

    @staticmethod
    def js_vars(player: Player):
        return dict(id_in_group=player.id_in_group, is_buyer=player.is_buyer)

    @staticmethod
    def get_timeout_seconds(player: Player):
        import time

        group = player.group
        return (group.start_timestamp + C.market_time) - time.time()


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [WaitToStart, Trading, ResultsWaitPage, Results]
