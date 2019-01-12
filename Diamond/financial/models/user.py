"""
ユーザーのモデル
"""
from django.db.models import Model, CharField


class User(Model):
    """
    ユーザーのモデルです

    Attributes
    ----------
    name : CharField
        [読み取り専用]
        ユーザー名
    password : CharField
        [書き込み専用]
        パスワード
    """

    # private fields

    _name = CharField(max_length=128)
    _password = CharField(max_length=128)  # TODO 平文にしない　

    # accessors

    @property
    def name(self) -> str:
        return self._name

    def password_setter(self, password: str):
        self._password = self.__digest(password)
    password = property().setter(password_setter)

    # public methods

    def __init__(self, name: str, password: str, *args, **kwargs):
        """
        Userインスタンスを生成します

        Parameters
        ----------
        name : str
            ユーザー名
        password : str
            パスワード
        """
        super().__init__(*args, **kwargs)
        self._name = name
        self.update(password=password)

    def __str__(self):
        return str(self.name)

    def isCorrect(self, password: str) -> bool:
        """
        入力されたパスワードが正しいかどうかを返します

        Parameters
        ----------
        password : str
            パスワード

        Return
        ------
        iscorrect : bool
            正しいかどうかの論理値
        """
        digested = self.__digest(password)
        result = (self._password == digested)
        return result

    def update(self, **kwargs):
        """
        ユーザーの内容を変更します
        必ず名前付き引数で指定してください
        引数が省略された項目は無視されます

        Parameters
        ----------
        password : str
            新しいパスワード
        """
        keys = kwargs.keys()
        if "password" in keys:
            self.password = kwargs.get("password")  # setterで書き込んでいる

    # private methods

    def __digest(self, password: str) -> str:
        digested = password  # TODO パスワードのダイジェスト化
        return digested
