# import random
# from uuid import uuid4

# from storage.dto import QAAnswerDTO, QAGroupDTO
# from storage.mongo_store import MongoStore


# def test_get_or_create_group(store: MongoStore, fake_group_dto: QAGroupDTO):
#     def count_documents():
#         return store._groups_collection.count_documents({})

#     base_id = uuid4()
#     assert count_documents() == 0
#     id = store.get_or_create_group(fake_group_dto, base_id)
#     assert count_documents() == 1
#     id2 = store.get_or_create_group(fake_group_dto, base_id)
#     assert count_documents() == 1
#     assert id == id2
#     new_dto = fake_group_dto.copy()
#     while new_dto.all_answers != fake_group_dto.all_answers:
#         random.shuffle(new_dto.all_answers)
#     id3 = store.get_or_create_group(new_dto, base_id)
#     assert count_documents() == 1
#     assert id3 == id


# def test_get_or_create_answer(store: MongoStore, fake_answer_dto: QAAnswerDTO):
#     def count_documents():
#         return store._answers_collection.count_documents({})

#     assert count_documents() == 0
#     qa1, is_new = store.get_or_create_qa(fake_answer_dto)
#     assert is_new is True
#     assert count_documents() == 1
#     qa2, is_new = store.get_or_create_qa(fake_answer_dto)
#     assert is_new is False
#     assert count_documents() == 1
#     qa1 == qa2
