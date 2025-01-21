import unittest
from unittest.mock import patch
import json
from io import StringIO
import datetime

from backend.app import app  # Asegúrate de que este import apunte correctamente a tu aplicación

class TranscriptApiTestCase(unittest.TestCase):
    def setUp(self):
        # Configura el cliente de pruebas de Flask
        self.app = app.test_client()

    def test_missing_video_id(self):
        """Verifica que sin el parámetro videoId se retorne un error 400."""
        response = self.app.get('/api/transcript')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode())
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Falta el parámetro videoId')

    @patch('app.YouTubeTranscriptApi.get_transcript')
    def test_transcript_with_timestamps(self, mock_get_transcript):
        """
        Verifica que, con el parámetro timestamps=true, se incluya 
        el minutaje en el transcript.
        """
        # Definir un transcript simulado
        mock_transcript = [
            {'start': 0, 'duration': 4, 'text': 'Test transcript text'}
        ]
        mock_get_transcript.return_value = mock_transcript

        response = self.app.get('/api/transcript?videoId=123&timestamps=true')
        self.assertEqual(response.status_code, 200)
        # Verificar que el encabezado de Content-Disposition contenga el nombre del archivo
        content_disposition = response.headers.get('Content-Disposition')
        self.assertIn('transcript_123.txt', content_disposition)
        # Verificar que el contenido incluya las marcas de tiempo
        # La marca debe formatearse como "[0:00:00 - 0:00:04] Test transcript text"
        expected_line = "[0:00:00 - 0:00:04] Test transcript text\n"
        response_text = response.data.decode()
        self.assertIn(expected_line, response_text)

    @patch('app.YouTubeTranscriptApi.get_transcript')
    def test_transcript_without_timestamps(self, mock_get_transcript):
        """
        Verifica que, con el parámetro timestamps=false, se genere el
        transcript sin marcas de tiempo.
        """
        mock_transcript = [
            {'start': 10, 'duration': 5, 'text': 'Text without timestamp'}
        ]
        mock_get_transcript.return_value = mock_transcript

        response = self.app.get('/api/transcript?videoId=456&timestamps=false')
        self.assertEqual(response.status_code, 200)
        # En este caso, se espera que el texto se devuelva sin marcas de tiempo
        expected_line = "Text without timestamp\n"
        response_text = response.data.decode()
        self.assertIn(expected_line, response_text)
        # Además, se puede verificar que no aparezcan corchetes (no se insertó la marca de tiempo)
        self.assertNotIn("[", response_text)
        
    @patch('app.YouTubeTranscriptApi.get_transcript')
    def test_transcript_api_error(self, mock_get_transcript):
        """
        Simula un error en YouTubeTranscriptApi.get_transcript y verifica 
        que se retorne un error 500.
        """
        mock_get_transcript.side_effect = Exception("API error")
        response = self.app.get('/api/transcript?videoId=789')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data.decode())
        self.assertIn('error', data)
        self.assertEqual(data['error'], "API error")

if __name__ == '__main__':
    unittest.main()
pyt