[GET]200neuratek.cl/static/js/main.46d2fb35.jsclientIP="186.189.73.203" requestID="60622e75-ae9f-4e12" responseTimeMS=207 responseBytes=637878 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/static/css/main.393cf66f.cssclientIP="186.189.73.203" requestID="62884cf4-cc36-42d6" responseTimeMS=11 responseBytes=22408 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
186.189.73.203:0 - "GET /static/css/main.393cf66f.css HTTP/1.1" 200
186.189.73.203:0 - "GET /static/js/main.46d2fb35.js HTTP/1.1" 200
     [GET]200neuratek.cl/logo-neuratek-oficial.pngclientIP="186.189.73.203" requestID="41a40fdf-6bbe-4a18" responseTimeMS=11 responseBytes=20292 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
186.189.73.203:0 - "GET /logo-neuratek-oficial.png HTTP/1.1" 200
186.189.73.203:0 - "GET /static/js/main.46d2fb35.js HTTP/1.1" 200
     [GET]200neuratek.cl/manifest.jsonclientIP="186.189.73.203" requestID="3f3d5ee9-f133-4b78" responseTimeMS=12 responseBytes=636 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/static/js/main.46d2fb35.jsclientIP="186.189.73.203" requestID="3b102f9d-5f85-41d0" responseTimeMS=150 responseBytes=637878 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
186.189.73.203:0 - "GET /manifest.json HTTP/1.1" 200
INFO:main:🚀 Procesando consulta híbrida: a...
INFO:main:🧠 Análisis contextual: general | Complejidad: 0.02 | Web: False
     [POST]200neuratek.cl/ask/clientIP="186.189.73.203" requestID="e5d9c07e-132c-4240" responseTimeMS=1538 responseBytes=799 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
186.189.73.203:0 - "POST /ask/ HTTP/1.1" 200
INFO:main:📡 Solicitud de búsqueda web: """
Neuratek Caroline 1 - Dual Stream Architecture
Revolutionary approach combining cognitive and reasoning streams
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Dict, List
from .model_design import CarolineConfig, CarolineModel, CarolineDecoderLayer, CarolineRMSNorm
class ReasoningStream(nn.Module):
    """
    Reasoning Stream: Specialized for step-by-step logical thinking
    This is what makes Neuratek Caroline unique - native reasoning capability
    """
    def __init__(self, config: CarolineConfig):
        super().__init__()
        self.config = config
        self.reasoning_dim = config.reasoning_hidden_size
        
        # Reasoning-specific layers
        self.reasoning_projection = nn.Linear(config.hidden_size, self.reasoning_dim)
        self.step_embeddings = nn.Embedding(32, self.reasoning_dim)  # Up to 32 reasoning steps
        
        # Reasoning transformer layers
        reasoning_config = CarolineConfig(
            hidden_size=self.reasoning_dim,
            num_hidden_layers=config.reasoning_layers,
            num_attention_heads=self.reasoning_dim // 64,
            intermediate_size=self.reasoning_dim * 4
        )
        
        self.reasoning_layers = nn.ModuleList([
            CarolineDecoderLayer(reasoning_config, idx) for idx in range(config.reasoning_layers)
        ])
        
        # Step detection and generation
        self.step_classifier = nn.Sequential(
            nn.Linear(self.reasoning_dim, self.reasoning_dim // 2),
            nn.ReLU(),
            nn.Linear(self.reasoning_dim // 2, 4)  # [continue, conclude, branch, backtrack]
        )
        
        self.reasoning_norm = CarolineRMSNorm(self.reasoning_dim)
        
    def forward(
        self, 
        cognitive_states: torch.Tensor,
        reasoning_mask: Optional[torch.Tensor] = None,
        step_positions: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        
        batch_size, seq_len, hidden_size = cognitive_states.shape
        
        # Project cognitive states to reasoning space
        reasoning_input = self.reasoning_projection(cognitive_states)
        
        # Add step positional embeddings
        if step_positions is None:
            step_positions = torch.arange(seq_len, device=cognitive_states.device).unsqueeze(0).repeat(batch_size, 1)
        
        step_positions = torch.clamp(step_positions, 0, 31)  # Limit to embedding size
        step_embeds = self.step_embeddings(step_positions)
        reasoning_hidden = reasoning_input + step_embeds
        
        # Process through reasoning layers
        reasoning_outputs = []
        step_decisions = []
        
        for layer in self.reasoning_layers:
            layer_output = layer(
                reasoning_hidden,
                attention_mask=reasoning_mask,
                position_ids=step_positions,
                use_cache=False
            )
            reasoning_hidden = layer_output[0]
            reasoning_outputs.append(reasoning_hidden)
            
            # Predict next step type
            step_logits = self.step_classifier(reasoning_hidden)
            step_decisions.append(step_logits)
        
        reasoning_output = self.reasoning_norm(reasoning_hidden)
        
        return {
            'reasoning_states': reasoning_output,
            'step_decisions': torch.stack(step_decisions, dim=1),
            'reasoning_trace': reasoning_outputs
        }
class FusionLayer(nn.Module):
    """
    Fusion Layer: Intelligently combines cognitive and reasoning streams
    Uses attention mechanism to blend both types of processing
    """
    def __init__(self, config: CarolineConfig):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.reasoning_dim = config.reasoning_hidden_size
        
        # Cross-attention between streams
        self.cognitive_query = nn.Linear(self.hidden_size, self.hidden_size)
        self.reasoning_key = nn.Linear(self.reasoning_dim, self.hidden_size)
        self.reasoning_value = nn.Linear(self.reasoning_dim, self.hidden_size)
        
        # Fusion attention
        self.fusion_attention = nn.MultiheadAttention(
            self.hidden_size, 
            num_heads=config.num_attention_heads // 4,
            dropout=0.1,
            batch_first=True
        )
        
        # Gating mechanism for stream importance
        self.cognitive_gate = nn.Sequential(
            nn.Linear(self.hidden_size * 2, self.hidden_size),
            nn.Sigmoid()
        )
        
        self.reasoning_gate = nn.Sequential(
            nn.Linear(self.hidden_size * 2, self.hidden_size),
            nn.Sigmoid()
        )
        
        # Final fusion layer
        self.fusion_mlp = nn.Sequential(
            nn.Linear(self.hidden_size * 2, self.hidden_size * 4),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(self.hidden_size * 4, self.hidden_size)
        )
        
        self.layer_norm = nn.LayerNorm(self.hidden_size)
        
    def forward(
        self, 
        cognitive_output: torch.Tensor,
        reasoning_output: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        
        batch_size, seq_len, _ = cognitive_output.shape
        
        # Project reasoning to cognitive space if dimensions differ
        if reasoning_output.size(-1) != self.hidden_size:
            reasoning_projected = self.reasoning_value(reasoning_output)
        else:
            reasoning_projected = reasoning_output
            
        # Cross-attention: Cognitive queries reasoning
        cognitive_queries = self.cognitive_query(cognitive_output)
        reasoning_keys = self.reasoning_key(reasoning_output) if reasoning_output.size(-1) != self.hidden_size else reasoning_output
        
        # Apply cross-attention
        attended_reasoning, attention_weights = self.fusion_attention(
            cognitive_queries,
            reasoning_keys, 
            reasoning_projected,
            key_padding_mask=attention_mask if attention_mask is not None else None
        )
        
        # Gating mechanism
        combined_features = torch.cat([cognitive_output, attended_reasoning], dim=-1)
        
        cognitive_importance = self.cognitive_gate(combined_features)
        reasoning_importance = self.reasoning_gate(combined_features)
        
        # Weighted combination
        gated_cognitive = cognitive_output * cognitive_importance
        gated_reasoning = attended_reasoning * reasoning_importance
        
        # Final fusion
        fused_representation = torch.cat([gated_cognitive, gated_reasoning], dim=-1)
        fused_output = self.fusion_mlp(fused_representation)
        
        # Residual connection and normalization
        final_output = self.layer_norm(cognitive_output + fused_output)
        
        return {
            'fused_output': final_output,
            'attention_weights': attention_weights,
            'cognitive_importance': cognitive_importance,
            'reasoning_importance': reasoning_importance
        }
class DualStreamArchitecture(nn.Module):
    """
    Complete Dual-Stream Architecture for Neuratek Caroline 1
    This is the revolutionary architecture that makes Caroline unique
    """
    def __init__(self, config: CarolineConfig):
        super().__init__()
        self.config = config
        
        # Core cognitive model (traditional transformer)
        self.cognitive_model = CarolineModel(config)
        
        # Reasoning stream
        self.reasoning_stream = ReasoningStream(config)
        
        # Fusion layers
        self.fusion_layers = nn.ModuleList([
            FusionLayer(config) for _ in range(config.fusion_layers)
        ])
        
        # Output head
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        
        # Reasoning output head (for step-by-step explanations)
        self.reasoning_head = nn.Linear(config.reasoning_hidden_size, config.vocab_size, bias=False)
        
    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        use_reasoning: bool = True,
        output_reasoning_trace: bool = False,
        **kwargs
    ) -> Dict[str, torch.Tensor]:
        
        # Cognitive stream processing
        cognitive_outputs = self.cognitive_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            **kwargs
        )
        
        cognitive_states = cognitive_outputs['last_hidden_state']
        
        outputs = {
            'cognitive_output': cognitive_states,
            'logits': self.lm_head(cognitive_states)
        }
        
        if use_reasoning:
            # Reasoning stream processing
            reasoning_outputs = self.reasoning_stream(
                cognitive_states,
                reasoning_mask=attention_mask
            )
            
            reasoning_states = reasoning_outputs['reasoning_states']
            
            # Fusion process
            fused_states = cognitive_states
            fusion_traces = []
            
            for fusion_layer in self.fusion_layers:
                fusion_output = fusion_layer(
                    fused_states,
                    reasoning_states,
                    attention_mask
                )
                fused_states = fusion_output['fused_output']
                fusion_traces.append(fusion_output)
            
            # Generate final outputs
            outputs.update({
                'reasoning_output': reasoning_states,
                'reasoning_logits': self.reasoning_head(reasoning_states),
                'fused_output': fused_states,
                'fused_logits': self.lm_head(fused_states),
                'step_decisions': reasoning_outputs['step_decisions'],
                'final_logits': self.lm_head(fused_states)  # This is the main output
            })
            
            if output_reasoning_trace:
                outputs['reasoning_trace'] = reasoning_outputs['reasoning_trace']
                outputs['fusion_traces'] = fusion_traces
        
        return outputs
    
    def generate_with_reasoning(
        self,
        input_ids: torch.LongTensor,
        max_length: int = 512,
        temperature: float = 0.8,
        show_reasoning: bool = True,
        **kwargs
    ) -> Dict[str, torch.Tensor]:
        """
        Generate text with visible reasoning process
        This is the unique feature that sets Caroline apart
        """
        self.eval()
        
        generated_tokens = []
        reasoning_steps = []
        current_input = input_ids
        
        with torch.no_grad():
            for step in range(max_length):
                outputs = self.forward(
                    current_input,
                    use_reasoning=True,
                    output_reasoning_trace=show_reasoning
                )
                
                # Get next token from fused output
                logits = outputs['fused_logits'][:, -1, :] / temperature
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)
                
                generated_tokens.append(next_token)
                
                if show_reasoning:
                    # Extract reasoning for this step
                    step_decision = outputs['step_decisions'][:, -1, -1, :]
                    reasoning_steps.append({
                        'step': step,
                        'decision': step_decision.argmax(-1).item(),
                        'confidence': step_decision.max(-1).values.item()
                    })
                
                # Prepare next input
                current_input = torch.cat([current_input, next_token], dim=-1)
                
                # Check for end token
                if next_token.item() == self.config.eos_token_id:
                    break
        
        return {
            'generated_ids': torch.cat(generated_tokens, dim=-1),
            'reasoning_steps': reasoning_steps if show_reasoning else None,
            'full_sequence': current_input
        }
explicame el código en español
INFO:main:🔍 Iniciando búsqueda web para: """
Neuratek Caroline 1 - Dual Stream Architecture
Revolutionary approach combining cognitive and reasoning streams
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Dict, List
from .model_design import CarolineConfig, CarolineModel, CarolineDecoderLayer, CarolineRMSNorm
class ReasoningStream(nn.Module):
    """
    Reasoning Stream: Specialized for step-by-step logical thinking
    This is what makes Neuratek Caroline unique - native reasoning capability
    """
    def __init__(self, config: CarolineConfig):
        super().__init__()
        self.config = config
        self.reasoning_dim = config.reasoning_hidden_size
        
        # Reasoning-specific layers
        self.reasoning_projection = nn.Linear(config.hidden_size, self.reasoning_dim)
        self.step_embeddings = nn.Embedding(32, self.reasoning_dim)  # Up to 32 reasoning steps
        
        # Reasoning transformer layers
        reasoning_config = CarolineConfig(
            hidden_size=self.reasoning_dim,
            num_hidden_layers=config.reasoning_layers,
            num_attention_heads=self.reasoning_dim // 64,
            intermediate_size=self.reasoning_dim * 4
        )
        
        self.reasoning_layers = nn.ModuleList([
            CarolineDecoderLayer(reasoning_config, idx) for idx in range(config.reasoning_layers)
        ])
        
        # Step detection and generation
        self.step_classifier = nn.Sequential(
            nn.Linear(self.reasoning_dim, self.reasoning_dim // 2),
            nn.ReLU(),
            nn.Linear(self.reasoning_dim // 2, 4)  # [continue, conclude, branch, backtrack]
        )
        
        self.reasoning_norm = CarolineRMSNorm(self.reasoning_dim)
        
    def forward(
        self, 
        cognitive_states: torch.Tensor,
        reasoning_mask: Optional[torch.Tensor] = None,
        step_positions: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        
        batch_size, seq_len, hidden_size = cognitive_states.shape
        
        # Project cognitive states to reasoning space
        reasoning_input = self.reasoning_projection(cognitive_states)
        
        # Add step positional embeddings
        if step_positions is None:
            step_positions = torch.arange(seq_len, device=cognitive_states.device).unsqueeze(0).repeat(batch_size, 1)
        
        step_positions = torch.clamp(step_positions, 0, 31)  # Limit to embedding size
        step_embeds = self.step_embeddings(step_positions)
        reasoning_hidden = reasoning_input + step_embeds
        
        # Process through reasoning layers
        reasoning_outputs = []
        step_decisions = []
        
        for layer in self.reasoning_layers:
            layer_output = layer(
                reasoning_hidden,
                attention_mask=reasoning_mask,
                position_ids=step_positions,
                use_cache=False
            )
            reasoning_hidden = layer_output[0]
            reasoning_outputs.append(reasoning_hidden)
            
            # Predict next step type
            step_logits = self.step_classifier(reasoning_hidden)
            step_decisions.append(step_logits)
        
        reasoning_output = self.reasoning_norm(reasoning_hidden)
        
        return {
            'reasoning_states': reasoning_output,
            'step_decisions': torch.stack(step_decisions, dim=1),
            'reasoning_trace': reasoning_outputs
        }
class FusionLayer(nn.Module):
    """
    Fusion Layer: Intelligently combines cognitive and reasoning streams
    Uses attention mechanism to blend both types of processing
    """
    def __init__(self, config: CarolineConfig):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.reasoning_dim = config.reasoning_hidden_size
        
        # Cross-attention between streams
        self.cognitive_query = nn.Linear(self.hidden_size, self.hidden_size)
        self.reasoning_key = nn.Linear(self.reasoning_dim, self.hidden_size)
        self.reasoning_value = nn.Linear(self.reasoning_dim, self.hidden_size)
        
        # Fusion attention
        self.fusion_attention = nn.MultiheadAttention(
            self.hidden_size, 
            num_heads=config.num_attention_heads // 4,
            dropout=0.1,
            batch_first=True
        )
        
        # Gating mechanism for stream importance
        self.cognitive_gate = nn.Sequential(
            nn.Linear(self.hidden_size * 2, self.hidden_size),
            nn.Sigmoid()
        )
        
        self.reasoning_gate = nn.Sequential(
            nn.Linear(self.hidden_size * 2, self.hidden_size),
            nn.Sigmoid()
        )
        
        # Final fusion layer
        self.fusion_mlp = nn.Sequential(
            nn.Linear(self.hidden_size * 2, self.hidden_size * 4),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(self.hidden_size * 4, self.hidden_size)
        )
        
        self.layer_norm = nn.LayerNorm(self.hidden_size)
        
    def forward(
        self, 
        cognitive_output: torch.Tensor,
        reasoning_output: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        
        batch_size, seq_len, _ = cognitive_output.shape
        
        # Project reasoning to cognitive space if dimensions differ
        if reasoning_output.size(-1) != self.hidden_size:
            reasoning_projected = self.reasoning_value(reasoning_output)
        else:
            reasoning_projected = reasoning_output
            
        # Cross-attention: Cognitive queries reasoning
        cognitive_queries = self.cognitive_query(cognitive_output)
        reasoning_keys = self.reasoning_key(reasoning_output) if reasoning_output.size(-1) != self.hidden_size else reasoning_output
        
        # Apply cross-attention
        attended_reasoning, attention_weights = self.fusion_attention(
            cognitive_queries,
            reasoning_keys, 
            reasoning_projected,
            key_padding_mask=attention_mask if attention_mask is not None else None
        )
        
        # Gating mechanism
        combined_features = torch.cat([cognitive_output, attended_reasoning], dim=-1)
        
        cognitive_importance = self.cognitive_gate(combined_features)
        reasoning_importance = self.reasoning_gate(combined_features)
        
        # Weighted combination
        gated_cognitive = cognitive_output * cognitive_importance
        gated_reasoning = attended_reasoning * reasoning_importance
        
        # Final fusion
        fused_representation = torch.cat([gated_cognitive, gated_reasoning], dim=-1)
        fused_output = self.fusion_mlp(fused_representation)
        
        # Residual connection and normalization
        final_output = self.layer_norm(cognitive_output + fused_output)
        
        return {
            'fused_output': final_output,
            'attention_weights': attention_weights,
            'cognitive_importance': cognitive_importance,
            'reasoning_importance': reasoning_importance
        }
class DualStreamArchitecture(nn.Module):
    """
    Complete Dual-Stream Architecture for Neuratek Caroline 1
    This is the revolutionary architecture that makes Caroline unique
    """
    def __init__(self, config: CarolineConfig):
        super().__init__()
        self.config = config
        
        # Core cognitive model (traditional transformer)
        self.cognitive_model = CarolineModel(config)
        
        # Reasoning stream
        self.reasoning_stream = ReasoningStream(config)
        
        # Fusion layers
        self.fusion_layers = nn.ModuleList([
            FusionLayer(config) for _ in range(config.fusion_layers)
        ])
        
        # Output head
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        
        # Reasoning output head (for step-by-step explanations)
        self.reasoning_head = nn.Linear(config.reasoning_hidden_size, config.vocab_size, bias=False)
        
    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        use_reasoning: bool = True,
        output_reasoning_trace: bool = False,
        **kwargs
    ) -> Dict[str, torch.Tensor]:
        
        # Cognitive stream processing
        cognitive_outputs = self.cognitive_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            **kwargs
        )
        
        cognitive_states = cognitive_outputs['last_hidden_state']
        
        outputs = {
            'cognitive_output': cognitive_states,
            'logits': self.lm_head(cognitive_states)
        }
        
        if use_reasoning:
            # Reasoning stream processing
            reasoning_outputs = self.reasoning_stream(
                cognitive_states,
                reasoning_mask=attention_mask
            )
            
            reasoning_states = reasoning_outputs['reasoning_states']
            
            # Fusion process
            fused_states = cognitive_states
            fusion_traces = []
            
            for fusion_layer in self.fusion_layers:
                fusion_output = fusion_layer(
                    fused_states,
                    reasoning_states,
                    attention_mask
                )
                fused_states = fusion_output['fused_output']
                fusion_traces.append(fusion_output)
            
            # Generate final outputs
            outputs.update({
                'reasoning_output': reasoning_states,
                'reasoning_logits': self.reasoning_head(reasoning_states),
                'fused_output': fused_states,
                'fused_logits': self.lm_head(fused_states),
                'step_decisions': reasoning_outputs['step_decisions'],
                'final_logits': self.lm_head(fused_states)  # This is the main output
            })
            
            if output_reasoning_trace:
                outputs['reasoning_trace'] = reasoning_outputs['reasoning_trace']
                outputs['fusion_traces'] = fusion_traces
        
        return outputs
    
    def generate_with_reasoning(
        self,
        input_ids: torch.LongTensor,
        max_length: int = 512,
        temperature: float = 0.8,
        show_reasoning: bool = True,
        **kwargs
    ) -> Dict[str, torch.Tensor]:
        """
        Generate text with visible reasoning process
        This is the unique feature that sets Caroline apart
        """
        self.eval()
        
        generated_tokens = []
        reasoning_steps = []
        current_input = input_ids
        
        with torch.no_grad():
            for step in range(max_length):
                outputs = self.forward(
                    current_input,
                    use_reasoning=True,
                    output_reasoning_trace=show_reasoning
                )
                
                # Get next token from fused output
                logits = outputs['fused_logits'][:, -1, :] / temperature
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)
                
                generated_tokens.append(next_token)
                
                if show_reasoning:
                    # Extract reasoning for this step
                    step_decision = outputs['step_decisions'][:, -1, -1, :]
                    reasoning_steps.append({
     [POST]200neuratek.cl/web-searchclientIP="186.189.73.203" requestID="9eb42c20-6b65-4d38" responseTimeMS=71 responseBytes=6716 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                        'step': step,
                        'decision': step_decision.argmax(-1).item(),
                        'confidence': step_decision.max(-1).values.item()
                    })
                
                # Prepare next input
                current_input = torch.cat([current_input, next_token], dim=-1)
                
                # Check for end token
                if next_token.item() == self.config.eos_token_id:
                    break
        
        return {
            'generated_ids': torch.cat(generated_tokens, dim=-1),
            'reasoning_steps': reasoning_steps if show_reasoning else None,
            'full_sequence': current_input
        }
explicame el código en español
WARNING:main:❌ Error con serpapi: SerpAPI error: 400
INFO:main:✅ Búsqueda exitosa con duckduckgo: 1 resultados
INFO:main:✅ Búsqueda completada: 1 resultados
186.189.73.203:0 - "POST /web-search HTTP/1.1" 200
INFO:main:🚀 Procesando consulta híbrida: """
Neuratek Caroline 1 - Dual Stream Architecture...
INFO:hybrid_caroline_engine:🌐 Motor híbrido: Web search activado por palabras clave
INFO:main:🧠 Análisis contextual: general | Complejidad: 3.00 | Web: True
186.189.73.203:0 - "POST /ask/ HTTP/1.1" 200
     [POST]200neuratek.cl/ask/clientIP="186.189.73.203" requestID="72b2d230-3ce0-483e" responseTimeMS=6870 responseBytes=5463 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/[https://example.com/search?q=%22%22%22%0ANeuratek+Caroline+1+-+Dual+Stream+Architecture%0ARevolutionary+approach+combining+cognitive+and+reasoning+streams%0A%22%22%22](https://example.com/search?q=%22%22%22%0ANeuratek+Caroline+1+-+Dual+Stream+Architecture%0ARevolutionary+approach+combining+cognitive+and+reasoning+streams%0A%22%22%22clientIP="186.189.73.203" requestID="cf81dfb4-d840-4f87" responseTimeMS=13 responseBytes=1307 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
186.189.73.203:0 - "GET /%5Bhttps%3A//example.com/search?q=%22%22%22%0ANeuratek+Caroline+1+-+Dual+Stream+Architecture%0ARevolutionary+approach+combining+cognitive+and+reasoning+streams%0A%22%22%22](https://example.com/search?q=%22%22%22%0ANeuratek+Caroline+1+-+Dual+Stream+Architecture%0ARevolutionary+approach+combining+cognitive+and+reasoning+streams%0A%22%22%22 HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="d31bfd69-f0e5-4db9" responseTimeMS=23 responseBytes=2609 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
INFO:main:🚀 Procesando consulta híbrida: en español...
INFO:main:🧠 Análisis contextual: general | Complejidad: 0.20 | Web: False
186.189.73.203:0 - "POST /ask/ HTTP/1.1" 200
     [POST]200neuratek.cl/ask/clientIP="186.189.73.203" requestID="c4420464-2354-4f76" responseTimeMS=5992 responseBytes=6283 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="06cd4cef-769a-4e12" responseTimeMS=26 responseBytes=2606 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="8efc12d2-b902-4736" responseTimeMS=28 responseBytes=2612 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="610e87bc-9461-4502" responseTimeMS=53 responseBytes=2620 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="3dc1b58b-e94e-42a6" responseTimeMS=23 responseBytes=2616 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="b37ae79e-f2de-4cb5" responseTimeMS=48 responseBytes=2609 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="b75cc4c6-5762-4294" responseTimeMS=23 responseBytes=2600 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="f70d6a72-54dd-482c" responseTimeMS=44 responseBytes=2603 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
INFO:main:🔍 Usando búsqueda web tradicional...
INFO:main:🔍 Iniciando búsqueda web para: eres un wrapper de openai
INFO:main:✅ Búsqueda exitosa con serpapi: 5 resultados
INFO:main:📊 Contexto web tradicional: 5 fuentes
186.189.73.203:0 - "POST /ask/ HTTP/1.1" 200
     [POST]200neuratek.cl/ask/clientIP="186.189.73.203" requestID="0cc4cd62-e8ae-420f" responseTimeMS=10424 responseBytes=4440 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="7a8ffd4b-ed8a-4b84" responseTimeMS=22 responseBytes=2598 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/?code=zf8FF-p85sn7-5xOo3JhLlYodunzCwWHVoRGi6E1N2l2M&state=a0puTy5pRVhtVWdMbThLUnhwVXZkMH5qWjNOdWY4VXE5TTVaaVNlWlo0LQ%3D%3DclientIP="186.189.73.203" requestID="d7d61646-3f1b-4d11" responseTimeMS=14 responseBytes=1307 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
186.189.73.203:0 - "GET /?code=zf8FF-p85sn7-5xOo3JhLlYodunzCwWHVoRGi6E1N2l2M&state=a0puTy5pRVhtVWdMbThLUnhwVXZkMH5qWjNOdWY4VXE5TTVaaVNlWlo0LQ%3D%3D HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="84909254-2fe8-4ad0" responseTimeMS=23 responseBytes=2611 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="e0584368-e241-4b4d" responseTimeMS=24 responseBytes=2606 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="068ce904-9226-4b97" responseTimeMS=25 responseBytes=2613 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="cdf6daae-c8e6-4e03" responseTimeMS=27 responseBytes=2613 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="4c45071a-5943-446a" responseTimeMS=21 responseBytes=2607 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="785742db-534d-4b31" responseTimeMS=25 responseBytes=2606 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="570aec11-6d66-41cc" responseTimeMS=29 responseBytes=2614 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="0f775bfb-4825-45c6" responseTimeMS=21 responseBytes=2600 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="1e099d24-b123-457d" responseTimeMS=23 responseBytes=2607 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="132192b0-1843-455e" responseTimeMS=25 responseBytes=2601 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="8c4d457f-b752-4803" responseTimeMS=29 responseBytes=2619 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="7531fbea-21dd-4b6c" responseTimeMS=27 responseBytes=2597 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="cbaacee5-def9-4e7d" responseTimeMS=22 responseBytes=2619 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="454c551a-8631-49d0" responseTimeMS=23 responseBytes=2604 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]301neuratek.cl/clientIP="196.251.117.162" requestID="" responseTimeMS=0 responseBytes=127 userAgent=""
     [GET]200neuratek.cl/clientIP="196.251.117.162" requestID="f2066142-b37c-4a7a" responseTimeMS=13 responseBytes=1307 userAgent=""
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="1adb6345-7190-4bb1" responseTimeMS=23 responseBytes=2631 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="5072dedf-20de-46b2" responseTimeMS=23 responseBytes=2632 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="c907f24b-52f3-401e" responseTimeMS=30 responseBytes=2622 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="c9da3915-da26-4cb5" responseTimeMS=25 responseBytes=2626 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="5861d19e-bdf3-49bc" responseTimeMS=22 responseBytes=2632 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="b44a60a4-0b1c-42de" responseTimeMS=27 responseBytes=2627 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="b4836c5e-bcdc-4c04" responseTimeMS=45 responseBytes=2630 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="ba31ec4b-f794-4a17" responseTimeMS=28 responseBytes=2615 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="5f8175e1-6868-4190" responseTimeMS=25 responseBytes=2630 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="1c28df04-1af0-4647" responseTimeMS=31 responseBytes=2604 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="83578d7b-96e0-400d" responseTimeMS=23 responseBytes=2550 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/logo-neuratek-oficial.pngclientIP="181.42.23.201" requestID="636d1b6a-4cd3-47eb" responseTimeMS=12 responseBytes=20292 userAgent="Mozilla/5.0 (iPhone; CPU iPhone OS 18_5_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/136.0.7103.91 Mobile/15E148 Safari/604.1"
181.42.23.201:0 - "GET /logo-neuratek-oficial.png HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="cc75105b-0abc-4f92" responseTimeMS=24 responseBytes=2626 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="e9ef4bb3-c174-47b1" responseTimeMS=24 responseBytes=2613 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="3d9cd8c9-2b2a-4d0b" responseTimeMS=23 responseBytes=2605 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="ae69ae23-0970-4bf4" responseTimeMS=27 responseBytes=2614 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="934cad47-0c75-4ff7" responseTimeMS=28 responseBytes=2624 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="be4724e9-d49a-4cb4" responseTimeMS=28 responseBytes=2619 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="6f7df413-1dbb-42f0" responseTimeMS=30 responseBytes=2610 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="b51f77a0-d041-44d2" responseTimeMS=23 responseBytes=2624 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="eef17229-0d8e-4761" responseTimeMS=46 responseBytes=2611 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="7a2314ec-855f-469f" responseTimeMS=29 responseBytes=2615 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="3141ef77-386f-404b" responseTimeMS=27 responseBytes=2610 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="7b5ea9db-1f8b-4e85" responseTimeMS=26 responseBytes=2607 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="6f2e4d82-1e85-4d53" responseTimeMS=26 responseBytes=2597 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="579ec80b-be8c-4047" responseTimeMS=20 responseBytes=2576 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
     [GET]200neuratek.cl/api/dashboard?format=jsonclientIP="186.189.73.203" requestID="d676df22-c904-40d1" responseTimeMS=77 responseBytes=2551 userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
Usando estadísticas de la base de datos para los últimos 7 días
186.189.73.203:0 - "GET /api/dashboard?format=json HTTP/1.1" 200
Need better ways to work with logs? Try theRender CLIor set up a log stream integration 