from chia.wallet.puzzles.load_clvm import load_clvm
from chia.types.blockchain_format.program import Program
from chia.util.ints import uint64
from chia.wallet.puzzles.cat_loader import CAT_MOD

SINGLETON_MOD: Program = load_clvm("singleton_top_layer_v1_1.clvm")
SINGLETON_LAUNCHER: Program = load_clvm("singleton_launcher.clvm")
DAO_EPHEMERAL_VOTE_MOD: Program = load_clvm("dao_ephemeral_vote.clvm")
DAO_LOCKUP_MOD: Program = load_clvm("dao_lockup.clvm")
DAO_PROPOSAL_TIMER_MOD: Program = load_clvm("dao_proposal_timer.clvm")
DAO_PROPOSAL_MOD: Program = load_clvm("dao_proposal.clvm")
DAO_TREASURY_MOD: Program = load_clvm("dao_treasury.clvm")
P2_SINGLETON_MOD: Program = load_clvm("p2_singleton_or_delayed_puzhash.clvm")


def test_proposal():
    # SINGLETON_STRUCT
    # PROPOSAL_MOD_HASH
    # PROPOSAL_TIMER_MOD_HASH
    # CAT_MOD_HASH
    # EPHEMERAL_VOTE_PUZHASH  ; this is the mod already curried with what it needs - should still be a constant
    # CAT_TAIL
    # CURRENT_CAT_ISSUANCE
    # PROPOSAL_PASS_PERCENTAGE
    # TREASURY_ID
    # PROPOSAL_TIMELOCK
    # VOTES
    # INNERPUZ

    current_cat_issuance: uint64 = uint64(1000)
    proposal_pass_percentage: uint64 = uint64(15)
    CAT_TAIL: Program = Program.to("tail").get_tree_hash()
    treasury_id: Program = Program.to("treasury").get_tree_hash()
    LOCKUP_TIME: uint64 = uint64(200)

    # LOCKUP_MOD_HASH
    # EPHEMERAL_VOTE_MODHASH
    # CAT_MOD_HASH
    # CAT_TAIL
    # LOCKUP_TIME

    EPHEMERAL_VOTE_PUZHASH: Program = DAO_EPHEMERAL_VOTE_MOD.curry(
        DAO_LOCKUP_MOD.get_tree_hash(),
        DAO_EPHEMERAL_VOTE_MOD.get_tree_hash(),
        CAT_MOD.get_tree_hash(),
        CAT_TAIL,
        LOCKUP_TIME,
    ).get_tree_hash()

    singleton_id: Program = Program.to("singleton_id").get_tree_hash()
    singleton_struct: Program = Program.to(
        (SINGLETON_MOD.get_tree_hash(), (singleton_id, SINGLETON_LAUNCHER.get_tree_hash()))
    )
    full_proposal: Program = DAO_PROPOSAL_MOD.curry(
        singleton_struct,
        DAO_PROPOSAL_MOD.get_tree_hash(),
        DAO_PROPOSAL_TIMER_MOD.get_tree_hash(),
        CAT_MOD.get_tree_hash(),
        DAO_TREASURY_MOD.get_tree_hash(),
        EPHEMERAL_VOTE_PUZHASH,
        CAT_TAIL,
        current_cat_issuance,
        proposal_pass_percentage,
        treasury_id,
        LOCKUP_TIME,
        0,
        20,
        Program.to(1),
    )
    # vote_amount
    # vote_info
    # solution
    solution: Program = Program.to([10, 1, Program.to("vote_coin").get_tree_hash(), 0])
    conds: Program = full_proposal.run(solution)
    assert len(conds.as_python()) == 3
    solution: Program = Program.to(
        [0, 0, Program.to("vote_coin").get_tree_hash(), [[51, 0xCAFEF00D, 200]], P2_SINGLETON_MOD.get_tree_hash()]
    )
    full_proposal: Program = DAO_PROPOSAL_MOD.curry(
        singleton_struct,
        DAO_PROPOSAL_MOD.get_tree_hash(),
        DAO_PROPOSAL_TIMER_MOD.get_tree_hash(),
        CAT_MOD.get_tree_hash(),
        DAO_TREASURY_MOD.get_tree_hash(),
        EPHEMERAL_VOTE_PUZHASH,
        CAT_TAIL,
        current_cat_issuance,
        proposal_pass_percentage,
        treasury_id,
        LOCKUP_TIME,
        200,
        350,
        Program.to(1),
    )
    conds: Program = full_proposal.run(solution)
    assert len(conds.as_python()) == 5


def test_proposal_timer():
    current_cat_issuance: uint64 = uint64(1000)
    proposal_pass_percentage: uint64 = uint64(15)
    CAT_TAIL: Program = Program.to("tail").get_tree_hash()
    treasury_id: Program = Program.to("treasury").get_tree_hash()
    LOCKUP_TIME: uint64 = uint64(200)
    EPHEMERAL_VOTE_PUZHASH: Program = DAO_EPHEMERAL_VOTE_MOD.curry(
        DAO_LOCKUP_MOD.get_tree_hash(),
        DAO_EPHEMERAL_VOTE_MOD.get_tree_hash(),
        CAT_MOD.get_tree_hash(),
        CAT_TAIL,
        LOCKUP_TIME,
    ).get_tree_hash()
    singleton_id: Program = Program.to("singleton_id").get_tree_hash()
    singleton_struct: Program = Program.to(
        (SINGLETON_MOD.get_tree_hash(), (singleton_id, SINGLETON_LAUNCHER.get_tree_hash()))
    )
    # PROPOSAL_MOD_HASH
    # PROPOSAL_TIMER_MOD_HASH
    # CAT_MOD_HASH
    # EPHEMERAL_VOTE_PUZZLE_HASH
    # CAT_TAIL
    # CURRENT_CAT_ISSUANCE
    # PROPOSAL_TIMELOCK
    # PROPOSAL_PASS_PERCENTAGE
    # MY_PARENT_SINGLETON_STRUCT
    # TREASURY_ID
    proposal_timer_full: Program = DAO_PROPOSAL_TIMER_MOD.curry(
        DAO_PROPOSAL_MOD.get_tree_hash(),
        DAO_PROPOSAL_TIMER_MOD.get_tree_hash(),
        CAT_MOD.get_tree_hash(),
        EPHEMERAL_VOTE_PUZHASH,
        CAT_TAIL,
        current_cat_issuance,
        LOCKUP_TIME,
        proposal_pass_percentage,
        singleton_struct,
        treasury_id,
    )

    # proposal_current_votes
    # proposal_innerpuzhash
    # proposal_parent_id
    # proposal_amount

    solution: Program = Program.to([140, 180, Program.to(1).get_tree_hash(), Program.to("parent").get_tree_hash(), 23])
    conds: Program = proposal_timer_full.run(solution)
    assert len(conds.as_python()) == 4


def test_treasury():
    current_cat_issuance: uint64 = uint64(1000)
    proposal_pass_percentage: uint64 = uint64(15)
    CAT_TAIL: Program = Program.to("tail").get_tree_hash()
    LOCKUP_TIME: uint64 = uint64(200)
    EPHEMERAL_VOTE_PUZHASH: Program = DAO_EPHEMERAL_VOTE_MOD.curry(
        DAO_LOCKUP_MOD.get_tree_hash(),
        DAO_EPHEMERAL_VOTE_MOD.get_tree_hash(),
        CAT_MOD.get_tree_hash(),
        CAT_TAIL,
        LOCKUP_TIME,
    ).get_tree_hash()
    singleton_id: Program = Program.to("singleton_id").get_tree_hash()
    singleton_struct: Program = Program.to(
        (SINGLETON_MOD.get_tree_hash(), (singleton_id, SINGLETON_LAUNCHER.get_tree_hash()))
    )
    # SINGLETON_STRUCT
    # PROPOSAL_MOD_HASH
    # PROPOSAL_TIMER_MOD_HASH
    # EPHEMERAL_VOTE_PUZHASH  ; this is the mod fully curried - effectively still a constant
    # P2_SINGLETON_MOD
    # CAT_MOD_HASH
    # CAT_TAIL
    # CURRENT_CAT_ISSUANCE
    # PROPOSAL_PASS_PERCENTAGE
    # PROPOSAL_TIMELOCK
    full_treasury_puz: Program = DAO_TREASURY_MOD.curry(
        singleton_struct,
        DAO_PROPOSAL_MOD.get_tree_hash(),
        DAO_PROPOSAL_TIMER_MOD.get_tree_hash(),
        EPHEMERAL_VOTE_PUZHASH,
        P2_SINGLETON_MOD.get_tree_hash(),
        CAT_MOD.get_tree_hash(),
        CAT_TAIL,
        current_cat_issuance,
        proposal_pass_percentage,
        LOCKUP_TIME,
    )

    # amount_or_new_puzhash
    # new_amount
    # my_puzhash_or_proposal_id
    # proposal_innerpuz  ; if this variable is 0 then we do the "add_money" spend case
    # proposal_current_votes
    # proposal_total_votes

    solution: Program = Program.to([200, 300, full_treasury_puz.get_tree_hash(), 0])
    conds: Program = full_treasury_puz.run(solution)
    assert len(conds.as_python()) == 3

    solution: Program = Program.to(
        [
            0xFADEDDAB,
            300,
            Program.to("proposal_id").get_tree_hash(),
            Program.to("proposal_inner").get_tree_hash(),
            100,
            150,
        ]
    )
    conds: Program = full_treasury_puz.run(solution)
    assert len(conds.as_python()) == 4


def test_ephemeral_vote():
    CAT_TAIL: Program = Program.to("tail").get_tree_hash()
    LOCKUP_TIME: uint64 = uint64(200)
    full_ephemeral_vote_puzzle = DAO_EPHEMERAL_VOTE_MOD.curry(
        DAO_PROPOSAL_MOD.get_tree_hash(),
        SINGLETON_MOD.get_tree_hash(),
        SINGLETON_LAUNCHER.get_tree_hash(),
        DAO_LOCKUP_MOD.get_tree_hash(),
        DAO_EPHEMERAL_VOTE_MOD.get_tree_hash(),
        CAT_MOD.get_tree_hash(),
        CAT_TAIL,
        LOCKUP_TIME,
    )
    # return_address
    # proposal_id
    # previous_votes
    # my_amount  ; this is the weight of your vote
    # vote_info  ; this is the information about what to do with your vote  - atm just 1 for yes or 0 for no
    # pubkey
    # my_id
    # proposal_curry_vals
    solution: Program = Program.to(
        [0xDEADBEEF, [0xFADEDDAB], 20, 1, 0x12341234, "my_id", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
    )
    conds: Program = full_ephemeral_vote_puzzle.run(solution)
    assert len(conds.as_python()) == 7


def test_lockup():
    # LOCKUP_MOD_HASH
    # EPHEMERAL_VOTE_MODHASH
    # CAT_MOD_HASH
    # CAT_TAIL
    # RETURN_ADDRESS
    # PREVIOUS_VOTES
    # LOCKUP_TIME
    CAT_TAIL: Program = Program.to("tail").get_tree_hash()
    LOCKUP_TIME: uint64 = uint64(200)
    full_ephemeral_vote_puzzle: Program = DAO_EPHEMERAL_VOTE_MOD.curry(
        DAO_PROPOSAL_MOD.get_tree_hash(),
        SINGLETON_MOD.get_tree_hash(),
        SINGLETON_LAUNCHER.get_tree_hash(),
        DAO_LOCKUP_MOD.get_tree_hash(),
        DAO_EPHEMERAL_VOTE_MOD.get_tree_hash(),
        CAT_MOD.get_tree_hash(),
        CAT_TAIL,
        LOCKUP_TIME,
    )

    full_lockup_puz: Program = DAO_LOCKUP_MOD.curry(
        DAO_PROPOSAL_MOD.get_tree_hash(),
        SINGLETON_MOD.get_tree_hash(),
        SINGLETON_LAUNCHER.get_tree_hash(),
        DAO_LOCKUP_MOD.get_tree_hash(),
        full_ephemeral_vote_puzzle.get_tree_hash(),
        CAT_MOD.get_tree_hash(),
        CAT_TAIL,
        [0xFADEDDAB],
        LOCKUP_TIME,
        0x12341234,
    )

    # my_id  ; if my_id is 0 we do the return to return_address (exit voting mode) spend case
    # my_amount
    # new_proposal_vote_id_or_return_address
    # vote_info
    solution: Program = Program.to([0xDEADBEEF, 20, 0xBADDADAB, 1])
    conds: Program = full_lockup_puz.run(solution)
    assert len(conds.as_python()) == 5

    # TODO: test return spend case
    solution: Program = Program.to([0, 20, 0xBADDADAB])
    conds: Program = full_lockup_puz.run(solution)
    assert len(conds.as_python()) == 4