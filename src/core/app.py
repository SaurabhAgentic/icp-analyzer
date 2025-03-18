from flask import stream_with_context, Response
import asyncio

@app.route('/your-endpoint', methods=['POST'])
def your_endpoint():
    try:
        # Set a timeout for the entire operation
        timeout = app.config.get('REQUEST_TIMEOUT', 60)
        
        def generate():
            # Process data in chunks
            chunk_size = 1000
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                # Process chunk
                yield process_chunk(chunk)
        
        return Response(stream_with_context(generate()))
    
    except TimeoutError:
        return jsonify({'error': 'Operation timed out'}), 408
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 