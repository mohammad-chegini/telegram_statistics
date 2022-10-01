import json
import re
from pathlib import Path
from typing import Union

import arabic_reshaper
import demoji
from hazm import Normalizer, word_tokenize
from loguru import logger
from src.data import DATA_DIR
from wordcloud import WordCloud


class Chat_Statistics:
    """Generates chat statistics from a telegram chat json file
    """    
    def __init__(self, chat_json: Union[str, Path]):
        """
        :param chat_json (Union[str, Path]): path to telegram export json file
        """        

        # load chat data
        logger.info(f" loading chat data from {chat_json} ")
        with open(chat_json) as f:
            self.chat_data = json.load(f)

        self.normalizer=Normalizer()

        # load stop words
        logger.info(f" loading stop words from {DATA_DIR / 'stopwords.txt'} ")
        stop_words = open(DATA_DIR / 'stopwords.txt').readlines()
        stop_words = list(map(str.strip,stop_words))
        self.stop_words=list(map(self.normalizer.normalize,stop_words))

    # delete emoji
    def de_emojify(self, text):
        """Removes emojis and some special characters from the text. 
​
        :param text: Text that contains emoji 
        """
        regrex_pattern = re.compile(pattern = "[\u2069\u2066]+", flags = re.UNICODE)
        text = regrex_pattern.sub(r'', text)
        return demoji.replace(text, " ")



    def generate_word_cloud(self, output_dir:Union[str, Path]):
        """ generates a word cloud from the chat data

        Args:
            output_dir (Union[str, Path]): path to output directory for word cloud image
        """       
        logger.info(" loading text content... ")
        text_content=''

        for msg in self.chat_data['messages']:
            if type(msg['text']) is str:
                tokens = word_tokenize(msg['text'])
                tokens = list(filter(lambda item:item not in self.stop_words,tokens))          
                text_content += f" {' '.join(tokens)}"

        #normalize, reshape for final word cloud

        text_content = arabic_reshaper.reshape(self.de_emojify(text_content))
        text_content=self.normalizer.normalize(text_content)
        
        #generate word cloud
        logger.info(" generating word cloud... ")
        wordcloud = WordCloud(
            width=1200, height=1200,
            font_path=str(DATA_DIR /'Vazirmatn-Light.ttf'),
            background_color='white',
            max_font_size=150
            ).generate(text_content)

        logger.info(f" saving wordcloud to {output_dir} ")
        wordcloud.to_file(str(Path(output_dir) / "wordcloud.png"))




if __name__ == '__main__':
    chat_stats=Chat_Statistics(chat_json = DATA_DIR / 'chat.json')
    chat_stats.generate_word_cloud(output_dir= DATA_DIR)

    print('Done !')
