from django.db import models
from django.contrib.auth.models import User

class Survey(models.Model):
    
    title = models.CharField(max_length=100, verbose_name="Наименование")
    is_active = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = ("Опрос")
        verbose_name_plural = ("Опросы")
        
    def __str__(self):
        return f'{str(self.title)}'


class Question(models.Model):
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    prompt = models.CharField(max_length=128, verbose_name="Вопрос")
    
    class Meta:
        verbose_name = ("Вопрос")
        verbose_name_plural = ("Вопросы")
        
    def __str__(self):
        return f'{str(self.prompt)} : {str(self.survey)}'


class Option(models.Model):
   
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=128, verbose_name="Ответ")
    is_right = models.BooleanField(default=False, verbose_name="Правильный ли?")
    
    class Meta:
        verbose_name = ("Вариант ответа")
        verbose_name_plural = ("Варианты ответов")
    
    def __str__(self):
        return f'{str(self.text)} : {str(self.question)}'
    

class Submission(models.Model):

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)
    

class Answer(models.Model):
    
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)