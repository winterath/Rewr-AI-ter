from split import split_text
from embed_and_store import add_documents

test_text ='''The stars twinkled above like scattered diamonds, their light piercing the darkness with an elegance that could only be described as timeless. Below, the earth stirred in a quiet symphony, as if the very soil and trees were listening for a melody. In the distance, a river meandered lazily, its surface shimmering under the pale moonlight, as though the water itself was contemplating the weight of centuries. Every breath of air seemed filled with secrets, like the kind shared only between old friends. Time moved in slow motion here, like a forgotten page from a well-worn book, waiting to be read again and again.'''


user_id = '321'
document_id = '12345'
splits = split_text(test_text, user_id,document_id)
for split in splits:
    print(split.page_content[:50], split.metadata)

vector_ids = add_documents(splits)
print('------000000------')
print(vector_ids)